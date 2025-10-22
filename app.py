from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import requests
import xml.etree.ElementTree as ET
import os
import json
import gzip
from pathlib import Path
import threading
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'epg-merger-secret-key'

# Configuration
DATA_DIR = Path('data')
DATA_DIR.mkdir(exist_ok=True)
CONFIG_FILE = DATA_DIR / 'config.json'
EPG_FILES_DIR = DATA_DIR / 'epg_files'
EPG_FILES_DIR.mkdir(exist_ok=True)

# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.start()

# Global job status tracking
job_status = {
    'is_running': False,
    'current_step': '',
    'progress': 0,
    'total_steps': 0,
    'current_epg_file': '',
    'current_source': '',
    'sources_completed': 0,
    'total_sources': 0,
    'start_time': None,
    'end_time': None,
    'error': None
}
job_status_lock = threading.Lock()


def load_config():
    """Load configuration from file"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
    else:
        config = {
            'sources': [],
            'epg_files': [],
            'schedule_interval': 7200  # Default: 2 hours in seconds
        }
    
    # Migrate sources without IDs
    migrated = False
    for source in config.get('sources', []):
        if 'id' not in source:
            import uuid
            source['id'] = str(uuid.uuid4())
            migrated = True
    
    if migrated:
        save_config(config)
    
    return config


def save_config(config):
    """Save configuration to file"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)


def fetch_xml(url):
    """Fetch XML content from URL (handles both plain XML and gzipped .xml.gz files)"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        content = response.content
        
        # Check if content is gzipped (by URL extension or content)
        if url.endswith('.gz') or content[:2] == b'\x1f\x8b':
            # Decompress gzipped content
            content = gzip.decompress(content)
        
        return ET.fromstring(content)
    except Exception as e:
        print(f"Error fetching {url}: {str(e)}")
        return None


def update_source_last_fetched(source_id):
    """Update the last_fetched timestamp for a source"""
    config = load_config()
    sources = config.get('sources', [])
    
    for source in sources:
        if source.get('id') == source_id:
            source['last_fetched'] = datetime.now().isoformat()
            break
    
    config['sources'] = sources
    save_config(config)


def update_job_status(**kwargs):
    """Update job status with thread safety"""
    with job_status_lock:
        for key, value in kwargs.items():
            if key in job_status:
                job_status[key] = value


def get_job_status():
    """Get current job status"""
    with job_status_lock:
        return job_status.copy()


def merge_epg_file(epg_file_id):
    """
    Merge EPG XML files for a specific EPG file.
    This function always downloads fresh data from selected source URLs.
    """
    config = load_config()
    epg_files = config.get('epg_files', [])
    
    # Find the EPG file
    epg_file = None
    for ef in epg_files:
        if ef.get('id') == epg_file_id:
            epg_file = ef
            break
    
    if not epg_file:
        print(f"EPG file {epg_file_id} not found")
        return False
    
    selected_sources = epg_file.get('sources', [])
    if not selected_sources:
        print(f"No sources selected for EPG file {epg_file.get('name', epg_file_id)}")
        return False
    
    epg_name = epg_file.get('name', epg_file_id)
    print(f"Starting EPG merge for '{epg_name}' at {datetime.now()} - Fetching fresh data from {len(selected_sources)} sources")
    
    # Update job status
    update_job_status(
        current_epg_file=epg_name,
        current_step=f"Starting merge for '{epg_name}'",
        total_sources=len(selected_sources),
        sources_completed=0
    )
    
    # Create root element
    root = ET.Element('tv')
    root.set('generator-info-name', 'EPG Merger')
    root.set('generator-info-url', 'http://localhost')
    
    channels = {}
    programmes = []
    
    # Get all sources
    all_sources = config.get('sources', [])
    
    # Fetch and parse each selected source
    for source_id in selected_sources:
        source = None
        for s in all_sources:
            if s.get('id') == source_id:
                source = s
                break
        
        if not source or not source.get('enabled', True):
            continue
            
        url = source.get('url')
        source_name = source.get('name', 'Unnamed Source')
        
        # Update job status for current source
        update_job_status(
            current_source=source_name,
            current_step=f"Downloading from {source_name}",
            sources_completed=job_status['sources_completed']
        )
        
        print(f"Fetching from {url}")
        xml_root = fetch_xml(url)
        
        if xml_root is None:
            update_job_status(
                current_step=f"Failed to fetch from {source_name}",
                sources_completed=job_status['sources_completed'] + 1
            )
            continue
        
        # Update the last_fetched timestamp for this source
        update_source_last_fetched(source_id)
        
        # Update job status after successful fetch
        update_job_status(
            current_step=f"Processing data from {source_name}",
            sources_completed=job_status['sources_completed'] + 1
        )
        
        # Extract channels (avoid duplicates)
        for channel in xml_root.findall('channel'):
            channel_id = channel.get('id')
            if channel_id and channel_id not in channels:
                channels[channel_id] = channel
        
        # Extract programmes
        for programme in xml_root.findall('programme'):
            programmes.append(programme)
    
    # Add channels to merged XML
    for channel in channels.values():
        root.append(channel)
    
    # Add programmes to merged XML
    for programme in programmes:
        root.append(programme)
    
    # Update job status for merging
    update_job_status(
        current_step=f"Merging data for '{epg_name}'"
    )
    
    # Create XML tree and write to file
    output_file = EPG_FILES_DIR / f"{epg_file_id}.xml"
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    tree.write(output_file, encoding='utf-8', xml_declaration=True)
    
    # Update job status for completion
    update_job_status(
        current_step=f"Completed '{epg_name}' - {len(channels)} channels, {len(programmes)} programmes"
    )
    
    print(f"EPG merge completed for '{epg_name}'. Total channels: {len(channels)}, Total programmes: {len(programmes)}")
    return True


def merge_all_epg_files():
    """Merge all EPG files"""
    config = load_config()
    epg_files = config.get('epg_files', [])
    
    if not epg_files:
        print("No EPG files configured")
        update_job_status(
            is_running=False,
            current_step="No EPG files configured",
            error="No EPG files configured"
        )
        return False
    
    # Initialize job status
    update_job_status(
        is_running=True,
        current_step="Starting EPG merge job",
        progress=0,
        total_steps=len(epg_files),
        start_time=datetime.now().isoformat(),
        end_time=None,
        error=None
    )
    
    success_count = 0
    for i, epg_file in enumerate(epg_files):
        epg_name = epg_file.get('name', epg_file.get('id'))
        update_job_status(
            progress=i,
            current_step=f"Processing EPG file {i+1}/{len(epg_files)}: {epg_name}"
        )
        
        if merge_epg_file(epg_file.get('id')):
            success_count += 1
    
    # Final job status
    update_job_status(
        is_running=False,
        current_step=f"Job completed - {success_count}/{len(epg_files)} EPG files processed",
        progress=len(epg_files),
        end_time=datetime.now().isoformat()
    )
    
    print(f"Completed merging {success_count}/{len(epg_files)} EPG files")
    return success_count > 0


def get_epg_file_stats(epg_file_id):
    """Get statistics about a specific EPG file"""
    epg_file_path = EPG_FILES_DIR / f"{epg_file_id}.xml"
    if not epg_file_path.exists():
        return None
    
    try:
        tree = ET.parse(epg_file_path)
        root = tree.getroot()
        
        channels = root.findall('channel')
        programmes = root.findall('programme')
        
        file_size = epg_file_path.stat().st_size
        last_modified = datetime.fromtimestamp(epg_file_path.stat().st_mtime)
        
        return {
            'channels_count': len(channels),
            'programmes_count': len(programmes),
            'file_size': file_size,
            'file_size_mb': round(file_size / (1024 * 1024), 2),
            'last_modified': last_modified.strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        print(f"Error getting stats for {epg_file_id}: {str(e)}")
        return None


def get_all_epg_stats():
    """Get statistics for all EPG files"""
    config = load_config()
    epg_files = config.get('epg_files', [])
    
    stats = []
    for epg_file in epg_files:
        epg_id = epg_file.get('id')
        file_stats = get_epg_file_stats(epg_id)
        
        stats.append({
            'id': epg_id,
            'name': epg_file.get('name'),
            'sources_count': len(epg_file.get('sources', [])),
            'stats': file_stats
        })
    
    return stats


def schedule_merge_job():
    """Schedule the merge job based on configuration"""
    config = load_config()
    interval = config.get('schedule_interval', 7200)
    
    # Remove existing jobs
    scheduler.remove_all_jobs()
    
    # Add new job
    scheduler.add_job(
        func=merge_all_epg_files,
        trigger='interval',
        seconds=interval,
        id='epg_merge_job',
        name='EPG Merge Job',
        replace_existing=True
    )
    print(f"Scheduled EPG merge every {interval} seconds ({interval//3600} hours, {(interval%3600)//60} minutes)")


@app.route('/')
def index():
    """Main page"""
    config = load_config()
    epg_stats = get_all_epg_stats()
    return render_template('index.html', config=config, epg_stats=epg_stats)


@app.route('/api/sources', methods=['GET'])
def get_sources():
    """Get all sources"""
    config = load_config()
    return jsonify(config.get('sources', []))


@app.route('/api/sources', methods=['POST'])
def add_source():
    """Add a new source"""
    data = request.get_json()
    url = data.get('url')
    name = data.get('name', '')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    config = load_config()
    sources = config.get('sources', [])
    
    # Check if URL already exists
    if any(s['url'] == url for s in sources):
        return jsonify({'error': 'URL already exists'}), 400
    
    # Generate unique ID for source
    import uuid
    source_id = str(uuid.uuid4())
    
    sources.append({
        'id': source_id,
        'url': url,
        'name': name,
        'enabled': True,
        'added_at': datetime.now().isoformat()
    })
    
    config['sources'] = sources
    save_config(config)
    
    return jsonify({'success': True, 'source_id': source_id})


@app.route('/api/sources/<source_id>', methods=['DELETE'])
def delete_source(source_id):
    """Delete a source"""
    config = load_config()
    sources = config.get('sources', [])
    
    # Find and remove source by ID
    sources = [s for s in sources if s.get('id') != source_id]
    
    # Also remove from all EPG files
    epg_files = config.get('epg_files', [])
    for epg_file in epg_files:
        epg_sources = epg_file.get('sources', [])
        epg_file['sources'] = [sid for sid in epg_sources if sid != source_id]
    
    config['sources'] = sources
    config['epg_files'] = epg_files
    save_config(config)
    
    return jsonify({'success': True})


@app.route('/api/sources/<source_id>/toggle', methods=['POST'])
def toggle_source(source_id):
    """Toggle source enabled/disabled"""
    config = load_config()
    sources = config.get('sources', [])
    
    for source in sources:
        if source.get('id') == source_id:
            source['enabled'] = not source.get('enabled', True)
            config['sources'] = sources
            save_config(config)
            return jsonify({'success': True})
    
    return jsonify({'error': 'Source not found'}), 404


@app.route('/api/merge', methods=['POST'])
def trigger_merge():
    """Manually trigger EPG merge for all files"""
    success = merge_all_epg_files()
    if success:
        return jsonify({'success': True, 'message': 'EPG merge completed'})
    else:
        return jsonify({'error': 'EPG merge failed'}), 500


@app.route('/api/epg-files', methods=['GET'])
def get_epg_files():
    """Get all EPG files"""
    config = load_config()
    return jsonify(config.get('epg_files', []))


@app.route('/api/epg-files', methods=['POST'])
def create_epg_file():
    """Create a new EPG file"""
    data = request.get_json()
    name = data.get('name', '').strip()
    
    if not name:
        return jsonify({'error': 'Name is required'}), 400
    
    config = load_config()
    epg_files = config.get('epg_files', [])
    
    # Check if name already exists
    if any(ef['name'] == name for ef in epg_files):
        return jsonify({'error': 'EPG file name already exists'}), 400
    
    # Generate unique ID
    import uuid
    epg_id = str(uuid.uuid4())
    
    epg_files.append({
        'id': epg_id,
        'name': name,
        'sources': [],
        'created_at': datetime.now().isoformat()
    })
    
    config['epg_files'] = epg_files
    save_config(config)
    
    return jsonify({'success': True, 'epg_id': epg_id})


@app.route('/api/epg-files/<epg_id>', methods=['DELETE'])
def delete_epg_file(epg_id):
    """Delete an EPG file"""
    config = load_config()
    epg_files = config.get('epg_files', [])
    
    # Find and remove EPG file
    epg_files = [ef for ef in epg_files if ef.get('id') != epg_id]
    
    # Delete the actual file
    epg_file_path = EPG_FILES_DIR / f"{epg_id}.xml"
    if epg_file_path.exists():
        epg_file_path.unlink()
    
    config['epg_files'] = epg_files
    save_config(config)
    
    return jsonify({'success': True})


@app.route('/api/epg-files/<epg_id>/merge', methods=['POST'])
def merge_single_epg_file(epg_id):
    """Manually trigger merge for a specific EPG file"""
    # Initialize job status for single file merge
    update_job_status(
        is_running=True,
        current_step=f"Starting merge for EPG file {epg_id}",
        progress=0,
        total_steps=1,
        start_time=datetime.now().isoformat(),
        end_time=None,
        error=None
    )
    
    success = merge_epg_file(epg_id)
    
    # Update final status
    update_job_status(
        is_running=False,
        end_time=datetime.now().isoformat()
    )
    
    if success:
        return jsonify({'success': True, 'message': 'EPG file merged successfully'})
    else:
        return jsonify({'error': 'EPG file merge failed'}), 500


@app.route('/api/epg-files/<epg_id>/sources', methods=['POST'])
def update_epg_sources(epg_id):
    """Update sources for an EPG file"""
    data = request.get_json()
    source_ids = data.get('sources', [])
    
    config = load_config()
    epg_files = config.get('epg_files', [])
    
    for epg_file in epg_files:
        if epg_file.get('id') == epg_id:
            epg_file['sources'] = source_ids
            config['epg_files'] = epg_files
            save_config(config)
            return jsonify({'success': True})
    
    return jsonify({'error': 'EPG file not found'}), 404


@app.route('/api/epg-files/<epg_id>/download')
def download_epg_file(epg_id):
    """Download a specific EPG file"""
    epg_file_path = EPG_FILES_DIR / f"{epg_id}.xml"
    if epg_file_path.exists():
        config = load_config()
        epg_files = config.get('epg_files', [])
        
        # Find EPG file name
        epg_name = "epg_file"
        for ef in epg_files:
            if ef.get('id') == epg_id:
                epg_name = ef.get('name', 'epg_file')
                break
        
        return send_file(epg_file_path, as_attachment=True, download_name=f'{epg_name}.xml')
    else:
        return "EPG file not found", 404


@app.route('/api/schedule', methods=['POST'])
def update_schedule():
    """Update schedule interval"""
    data = request.get_json()
    interval = data.get('interval')
    
    if not interval or interval < 60:
        return jsonify({'error': 'Interval must be at least 60 seconds'}), 400
    
    config = load_config()
    config['schedule_interval'] = interval
    save_config(config)
    
    schedule_merge_job()
    
    return jsonify({'success': True})


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get EPG statistics for all files"""
    stats = get_all_epg_stats()
    return jsonify(stats)


@app.route('/api/version', methods=['GET'])
def get_version():
    """Get application version"""
    return jsonify({
        'version': '1.0.0',
        'name': 'EPG Merger',
        'description': 'Multiple EPG XML file merger with scheduling'
    })


@app.route('/api/job-status', methods=['GET'])
def get_job_status_api():
    """Get current job status"""
    status = get_job_status()
    
    # Calculate progress percentage
    if status['total_steps'] > 0:
        status['progress_percentage'] = int((status['progress'] / status['total_steps']) * 100)
    else:
        status['progress_percentage'] = 0
    
    # Calculate elapsed time
    if status['start_time']:
        start_time = datetime.fromisoformat(status['start_time'])
        if status['end_time']:
            end_time = datetime.fromisoformat(status['end_time'])
            status['elapsed_time'] = str(end_time - start_time)
        else:
            status['elapsed_time'] = str(datetime.now() - start_time)
    else:
        status['elapsed_time'] = None
    
    return jsonify(status)


# Legacy download route for backward compatibility
@app.route('/download')
def download_epg():
    """Download first available EPG file (legacy route)"""
    config = load_config()
    epg_files = config.get('epg_files', [])
    
    if epg_files:
        epg_id = epg_files[0].get('id')
        epg_file_path = EPG_FILES_DIR / f"{epg_id}.xml"
        if epg_file_path.exists():
            epg_name = epg_files[0].get('name', 'epg_file')
            return send_file(epg_file_path, as_attachment=True, download_name=f'{epg_name}.xml')
    
    return "No EPG files available. Please create an EPG file and add sources first.", 404


@app.route('/api/sources/<source_id>/test', methods=['GET'])
def test_source(source_id):
    """Test a source and return its stats"""
    config = load_config()
    sources = config.get('sources', [])
    
    source = None
    for s in sources:
        if s.get('id') == source_id:
            source = s
            break
    
    if not source:
        return jsonify({'error': 'Source not found'}), 404
    
    url = source.get('url')
    
    try:
        print(f"Testing source: {url}")
        xml_root = fetch_xml(url)
        
        if xml_root is None:
            return jsonify({
                'success': False,
                'error': 'Failed to fetch or parse XML',
                'channels': 0,
                'programmes': 0
            })
        
        # Update the last_fetched timestamp for this source
        update_source_last_fetched(source_id)
        
        channels = xml_root.findall('channel')
        programmes = xml_root.findall('programme')
        
        return jsonify({
            'success': True,
            'channels': len(channels),
            'programmes': len(programmes),
            'url': url
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'channels': 0,
            'programmes': 0
        })


if __name__ == '__main__':
    # Schedule the merge job on startup
    config = load_config()
    if config.get('epg_files'):
        schedule_merge_job()
    
    # Run the app
    app.run(host='0.0.0.0', port=5000, debug=True)

