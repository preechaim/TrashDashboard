from flask import Flask, render_template, request, jsonify, send_from_directory
from datetime import datetime
import sqlite3
import os

app = Flask(__name__)
DATABASE = 'trashbin.db'

# Scope 3 Emissions Factors (kg CO2e per kg of waste)
# Based on EPA and industry standards
EMISSIONS_FACTORS = {
    'landfill': 0.5,  # kg CO2e per kg waste to landfill
    'recycling': 0.1,  # kg CO2e per kg recycling process
    'avoided': 2.0,   # kg CO2e avoided per kg recycled (avoided production emissions)
}

def calculate_co2_emissions(weight, waste_type, event_type='add'):
    """Calculate Scope 3 CO2 emissions based on waste type and weight"""
    if event_type == 'empty':
        # When emptying, calculate actual emissions
        if waste_type == 'normal':
            # Normal waste goes to landfill
            co2 = weight * EMISSIONS_FACTORS['landfill']
        else:  # recycle
            # Recycling has processing emissions but avoids production emissions
            co2 = (weight * EMISSIONS_FACTORS['recycling']) - (weight * EMISSIONS_FACTORS['avoided'])
        return co2
    return 0  # No emissions during 'add' events, only when waste is processed

def get_db_connection():
    """Create a database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create trashbin_status table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trashbin_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            normal_volume REAL DEFAULT 0,
            normal_weight REAL DEFAULT 0,
            recycle_volume REAL DEFAULT 0,
            recycle_weight REAL DEFAULT 0,
            normal_capacity REAL DEFAULT 100,
            recycle_capacity REAL DEFAULT 100,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create trash_logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trash_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            waste_type TEXT NOT NULL,
            volume REAL NOT NULL,
            weight REAL NOT NULL,
            event_type TEXT DEFAULT 'add',
            co2_emissions REAL DEFAULT 0,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create emissions_summary table for Scope 3 tracking
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emissions_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            total_co2_landfill REAL DEFAULT 0,
            total_co2_recycling REAL DEFAULT 0,
            total_co2_avoided REAL DEFAULT 0,
            net_co2_emissions REAL DEFAULT 0,
            total_waste_diverted REAL DEFAULT 0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Add event_type column if it doesn't exist (migration)
    try:
        cursor.execute("SELECT event_type FROM trash_logs LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE trash_logs ADD COLUMN event_type TEXT DEFAULT 'add'")
    
    # Add co2_emissions column if it doesn't exist (migration)
    try:
        cursor.execute("SELECT co2_emissions FROM trash_logs LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE trash_logs ADD COLUMN co2_emissions REAL DEFAULT 0")
    
    # Insert initial status if not exists
    cursor.execute('SELECT COUNT(*) FROM trashbin_status')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO trashbin_status 
            (normal_volume, normal_weight, recycle_volume, recycle_weight, 
             normal_capacity, recycle_capacity)
            VALUES (0, 0, 0, 0, 100, 100)
        ''')
    
    # Insert initial emissions summary if not exists
    cursor.execute('SELECT COUNT(*) FROM emissions_summary')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO emissions_summary 
            (total_co2_landfill, total_co2_recycling, total_co2_avoided, 
             net_co2_emissions, total_waste_diverted)
            VALUES (0, 0, 0, 0, 0)
        ''')
    
    conn.commit()
    conn.close()

@app.route('/')
def dashboard():
    """Render the dashboard page"""
    conn = None
    try:
        conn = get_db_connection()
        
        # Get current status
        status = conn.execute('SELECT * FROM trashbin_status ORDER BY id DESC LIMIT 1').fetchone()
        
        # Get emissions summary
        emissions = conn.execute('SELECT * FROM emissions_summary ORDER BY id DESC LIMIT 1').fetchone()
        
        # Get recent logs (last 20 entries)
        logs = conn.execute('''
            SELECT * FROM trash_logs 
            ORDER BY timestamp DESC 
            LIMIT 20
        ''').fetchall()
        
        # Get statistics
        stats = conn.execute('''
            SELECT 
                waste_type,
                COUNT(*) as count,
                SUM(volume) as total_volume,
                SUM(weight) as total_weight,
                AVG(volume) as avg_volume,
                AVG(weight) as avg_weight,
                SUM(co2_emissions) as total_co2
            FROM trash_logs
            GROUP BY waste_type
        ''').fetchall()
        
        # Calculate monthly trend data (last 30 days)
        monthly_emissions = conn.execute('''
            SELECT 
                DATE(timestamp) as date,
                waste_type,
                SUM(weight) as daily_weight,
                SUM(co2_emissions) as daily_co2
            FROM trash_logs
            WHERE timestamp >= date('now', '-30 days')
            GROUP BY DATE(timestamp), waste_type
            ORDER BY date DESC
        ''').fetchall()
        
        # Get hourly capacity data for today's chart
        hourly_capacity = conn.execute('''
            SELECT 
                strftime('%H:00', timestamp) as hour,
                waste_type,
                AVG(volume) as avg_volume,
                COUNT(*) as event_count
            FROM trash_logs
            WHERE DATE(timestamp) = DATE('now')
            GROUP BY strftime('%H', timestamp), waste_type
            ORDER BY hour
        ''').fetchall()
        
        # Get daily collected weight from last 7 days
        daily_weight_data = conn.execute('''
            SELECT 
                DATE(timestamp) as date,
                waste_type,
                SUM(CASE WHEN event_type = 'add' THEN weight ELSE 0 END) as total_weight
            FROM trash_logs
            WHERE timestamp >= date('now', '-7 days')
            GROUP BY DATE(timestamp), waste_type
            ORDER BY date ASC
        ''').fetchall()
        
        # Organize daily weight data
        daily_weights = {}
        for row in daily_weight_data:
            date = row['date']
            waste_type = row['waste_type']
            weight = row['total_weight']
            
            if date not in daily_weights:
                daily_weights[date] = {'normal': 0, 'recycle': 0}
            
            daily_weights[date][waste_type] = weight
        
        # Convert to list format for chart
        daily_capacity = []
        for date in sorted(daily_weights.keys()):
            daily_capacity.append({
                'date': date,
                'normal_weight': daily_weights[date].get('normal', 0),
                'recycle_weight': daily_weights[date].get('recycle', 0)
            })
        
        return render_template('dashboard.html', 
                             status=status, 
                             emissions=emissions,
                             logs=logs, 
                             stats=stats,
                             monthly_emissions=monthly_emissions,
                             hourly_capacity=hourly_capacity,
                             daily_capacity=daily_capacity)
    finally:
        if conn:
            conn.close()

@app.route('/api/trash', methods=['POST'])
def add_trash():
    """API endpoint to add trash entry"""
    conn = None
    try:
        data = request.get_json()
        
        waste_type = data.get('waste_type', '').lower()
        volume = float(data.get('volume', 0))
        weight = float(data.get('weight', 0))
        
        if waste_type not in ['normal', 'recycle']:
            return jsonify({'error': 'Invalid waste_type. Must be "normal" or "recycle"'}), 400
        
        if volume <= 0 or weight <= 0:
            return jsonify({'error': 'Volume and weight must be positive numbers'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Add log entry (no emissions during add, only during empty)
        cursor.execute('''
            INSERT INTO trash_logs (waste_type, volume, weight, event_type, co2_emissions)
            VALUES (?, ?, ?, 'add', 0)
        ''', (waste_type, volume, weight))
        
        # Update current status
        if waste_type == 'normal':
            cursor.execute('''
                UPDATE trashbin_status
                SET normal_volume = normal_volume + ?,
                    normal_weight = normal_weight + ?,
                    last_updated = CURRENT_TIMESTAMP
                WHERE id = (SELECT MAX(id) FROM trashbin_status)
            ''', (volume, weight))
        else:  # recycle
            cursor.execute('''
                UPDATE trashbin_status
                SET recycle_volume = recycle_volume + ?,
                    recycle_weight = recycle_weight + ?,
                    last_updated = CURRENT_TIMESTAMP
                WHERE id = (SELECT MAX(id) FROM trashbin_status)
            ''', (volume, weight))
        
        conn.commit()
        
        # Get updated status
        status = cursor.execute('SELECT * FROM trashbin_status ORDER BY id DESC LIMIT 1').fetchone()
        
        result = {
            'success': True,
            'message': f'{waste_type.capitalize()} waste added successfully',
            'current_status': {
                'normal_volume': status['normal_volume'],
                'normal_weight': status['normal_weight'],
                'recycle_volume': status['recycle_volume'],
                'recycle_weight': status['recycle_weight']
            }
        }
        
        return jsonify(result), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/reset', methods=['POST'])
def reset_bin():
    """API endpoint to reset/empty the trash bin"""
    conn = None
    try:
        data = request.get_json()
        waste_type = data.get('waste_type', 'both').lower()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if waste_type == 'normal':
            # Get current values before reset
            current = cursor.execute('SELECT normal_volume, normal_weight FROM trashbin_status ORDER BY id DESC LIMIT 1').fetchone()
            
            # Calculate emissions for landfill
            co2_emitted = calculate_co2_emissions(current['normal_weight'], 'normal', 'empty')
            
            cursor.execute('''
                UPDATE trashbin_status
                SET normal_volume = 0,
                    normal_weight = 0,
                    last_updated = CURRENT_TIMESTAMP
                WHERE id = (SELECT MAX(id) FROM trashbin_status)
            ''')
            
            # Log the empty event with emissions
            cursor.execute('''
                INSERT INTO trash_logs (waste_type, volume, weight, event_type, co2_emissions)
                VALUES ('normal', ?, ?, 'empty', ?)
            ''', (current['normal_volume'], current['normal_weight'], co2_emitted))
            
            # Update emissions summary
            cursor.execute('''
                UPDATE emissions_summary
                SET total_co2_landfill = total_co2_landfill + ?,
                    net_co2_emissions = net_co2_emissions + ?,
                    last_updated = CURRENT_TIMESTAMP
                WHERE id = (SELECT MAX(id) FROM emissions_summary)
            ''', (co2_emitted, co2_emitted))
            
        elif waste_type == 'recycle':
            # Get current values before reset
            current = cursor.execute('SELECT recycle_volume, recycle_weight FROM trashbin_status ORDER BY id DESC LIMIT 1').fetchone()
            
            # Calculate net emissions (negative because recycling avoids more emissions than it creates)
            co2_emitted = calculate_co2_emissions(current['recycle_weight'], 'recycle', 'empty')
            co2_avoided = current['recycle_weight'] * EMISSIONS_FACTORS['avoided']
            
            cursor.execute('''
                UPDATE trashbin_status
                SET recycle_volume = 0,
                    recycle_weight = 0,
                    last_updated = CURRENT_TIMESTAMP
                WHERE id = (SELECT MAX(id) FROM trashbin_status)
            ''')
            
            # Log the empty event with net emissions
            cursor.execute('''
                INSERT INTO trash_logs (waste_type, volume, weight, event_type, co2_emissions)
                VALUES ('recycle', ?, ?, 'empty', ?)
            ''', (current['recycle_volume'], current['recycle_weight'], co2_emitted))
            
            # Update emissions summary
            cursor.execute('''
                UPDATE emissions_summary
                SET total_co2_recycling = total_co2_recycling + ?,
                    total_co2_avoided = total_co2_avoided + ?,
                    net_co2_emissions = net_co2_emissions + ?,
                    total_waste_diverted = total_waste_diverted + ?,
                    last_updated = CURRENT_TIMESTAMP
                WHERE id = (SELECT MAX(id) FROM emissions_summary)
            ''', (abs(co2_emitted) if co2_emitted > 0 else 0, co2_avoided, co2_emitted, current['recycle_weight']))
            
        else:  # both
            # Get current values before reset
            current = cursor.execute('SELECT normal_volume, normal_weight, recycle_volume, recycle_weight FROM trashbin_status ORDER BY id DESC LIMIT 1').fetchone()
            
            # Calculate emissions for both bins
            normal_co2 = calculate_co2_emissions(current['normal_weight'], 'normal', 'empty')
            recycle_co2 = calculate_co2_emissions(current['recycle_weight'], 'recycle', 'empty')
            recycle_avoided = current['recycle_weight'] * EMISSIONS_FACTORS['avoided']
            
            cursor.execute('''
                UPDATE trashbin_status
                SET normal_volume = 0,
                    normal_weight = 0,
                    recycle_volume = 0,
                    recycle_weight = 0,
                    last_updated = CURRENT_TIMESTAMP
                WHERE id = (SELECT MAX(id) FROM trashbin_status)
            ''')
            
            # Log the empty events for both bins with emissions
            cursor.execute('''
                INSERT INTO trash_logs (waste_type, volume, weight, event_type, co2_emissions)
                VALUES ('normal', ?, ?, 'empty', ?)
            ''', (current['normal_volume'], current['normal_weight'], normal_co2))
            
            cursor.execute('''
                INSERT INTO trash_logs (waste_type, volume, weight, event_type, co2_emissions)
                VALUES ('recycle', ?, ?, 'empty', ?)
            ''', (current['recycle_volume'], current['recycle_weight'], recycle_co2))
            
            # Update emissions summary
            cursor.execute('''
                UPDATE emissions_summary
                SET total_co2_landfill = total_co2_landfill + ?,
                    total_co2_recycling = total_co2_recycling + ?,
                    total_co2_avoided = total_co2_avoided + ?,
                    net_co2_emissions = net_co2_emissions + ?,
                    total_waste_diverted = total_waste_diverted + ?,
                    last_updated = CURRENT_TIMESTAMP
                WHERE id = (SELECT MAX(id) FROM emissions_summary)
            ''', (normal_co2, abs(recycle_co2) if recycle_co2 > 0 else 0, recycle_avoided, normal_co2 + recycle_co2, current['recycle_weight']))
        
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': f'{waste_type.capitalize()} bin reset successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/status', methods=['GET'])
def get_status():
    """API endpoint to get current status"""
    conn = None
    try:
        conn = get_db_connection()
        status = conn.execute('SELECT * FROM trashbin_status ORDER BY id DESC LIMIT 1').fetchone()
        
        return jsonify({
            'normal_volume': status['normal_volume'],
            'normal_weight': status['normal_weight'],
            'recycle_volume': status['recycle_volume'],
            'recycle_weight': status['recycle_weight'],
            'normal_capacity': status['normal_capacity'],
            'recycle_capacity': status['recycle_capacity'],
            'last_updated': status['last_updated']
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/static/icon-192.png')
@app.route('/static/icon-512.png')
def serve_icon():
    """Serve the SVG icon for both sizes"""
    return send_from_directory('static', 'icon.svg', mimetype='image/svg+xml')

if __name__ == '__main__':
    # Initialize database on startup
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
