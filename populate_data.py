"""
Populate database with 7 days of dummy data for chart visualization
"""
import sqlite3
from datetime import datetime, timedelta
import random

DATABASE = 'trashbin.db'

def populate_dummy_data():
    """Add 7 days of sample data to the database"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    print("Adding 7 days of dummy data...")
    
    # Generate data for each of the past 7 days
    for day_offset in range(7, 0, -1):
        # Calculate the date
        target_date = datetime.now() - timedelta(days=day_offset)
        
        # Generate 2-4 normal waste entries per day
        num_normal_entries = random.randint(2, 4)
        for i in range(num_normal_entries):
            volume = round(random.uniform(5, 15), 2)
            weight = round(random.uniform(2, 8), 2)
            
            # Spread entries throughout the day
            hour = random.randint(6, 20)
            minute = random.randint(0, 59)
            timestamp = target_date.replace(hour=hour, minute=minute, second=0)
            
            cursor.execute('''
                INSERT INTO trash_logs (waste_type, volume, weight, event_type, co2_emissions, timestamp)
                VALUES (?, ?, ?, 'add', 0, ?)
            ''', ('normal', volume, weight, timestamp.strftime('%Y-%m-%d %H:%M:%S')))
            
            # Update running status
            cursor.execute('''
                UPDATE trashbin_status
                SET normal_volume = normal_volume + ?,
                    normal_weight = normal_weight + ?,
                    last_updated = ?
                WHERE id = (SELECT MAX(id) FROM trashbin_status)
            ''', (volume, weight, timestamp.strftime('%Y-%m-%d %H:%M:%S')))
        
        print(f"  ✓ Day {day_offset}: Added {num_normal_entries} normal waste entries")
        
        # Generate 1-3 recyclable waste entries per day
        num_recycle_entries = random.randint(1, 3)
        for i in range(num_recycle_entries):
            volume = round(random.uniform(3, 12), 2)
            weight = round(random.uniform(1, 5), 2)
            
            # Spread entries throughout the day
            hour = random.randint(7, 19)
            minute = random.randint(0, 59)
            timestamp = target_date.replace(hour=hour, minute=minute, second=0)
            
            cursor.execute('''
                INSERT INTO trash_logs (waste_type, volume, weight, event_type, co2_emissions, timestamp)
                VALUES (?, ?, ?, 'add', 0, ?)
            ''', ('recycle', volume, weight, timestamp.strftime('%Y-%m-%d %H:%M:%S')))
            
            # Update running status
            cursor.execute('''
                UPDATE trashbin_status
                SET recycle_volume = recycle_volume + ?,
                    recycle_weight = recycle_weight + ?,
                    last_updated = ?
                WHERE id = (SELECT MAX(id) FROM trashbin_status)
            ''', (volume, weight, timestamp.strftime('%Y-%m-%d %H:%M:%S')))
        
        print(f"  ✓ Day {day_offset}: Added {num_recycle_entries} recyclable waste entries")
        
        # Randomly empty bins every 2-3 days
        if day_offset % 2 == 0 and day_offset < 7:
            # Get current status
            status = cursor.execute('SELECT normal_volume, normal_weight, recycle_volume, recycle_weight FROM trashbin_status ORDER BY id DESC LIMIT 1').fetchone()
            
            if status:
                normal_weight = status[1]
                recycle_weight = status[3]
                
                # Calculate emissions
                normal_co2 = normal_weight * 0.5  # Landfill emissions
                recycle_co2 = (recycle_weight * 0.1) - (recycle_weight * 2.0)  # Net negative
                recycle_avoided = recycle_weight * 2.0
                
                timestamp = target_date.replace(hour=22, minute=0, second=0)
                
                # Log empty events
                cursor.execute('''
                    INSERT INTO trash_logs (waste_type, volume, weight, event_type, co2_emissions, timestamp)
                    VALUES ('normal', ?, ?, 'empty', ?, ?)
                ''', (status[0], normal_weight, normal_co2, timestamp.strftime('%Y-%m-%d %H:%M:%S')))
                
                cursor.execute('''
                    INSERT INTO trash_logs (waste_type, volume, weight, event_type, co2_emissions, timestamp)
                    VALUES ('recycle', ?, ?, 'empty', ?, ?)
                ''', (status[2], recycle_weight, recycle_co2, timestamp.strftime('%Y-%m-%d %H:%M:%S')))
                
                # Reset bins
                cursor.execute('''
                    UPDATE trashbin_status
                    SET normal_volume = 0,
                        normal_weight = 0,
                        recycle_volume = 0,
                        recycle_weight = 0,
                        last_updated = ?
                    WHERE id = (SELECT MAX(id) FROM trashbin_status)
                ''', (timestamp.strftime('%Y-%m-%d %H:%M:%S'),))
                
                # Update emissions summary
                cursor.execute('''
                    UPDATE emissions_summary
                    SET total_co2_landfill = total_co2_landfill + ?,
                        total_co2_recycling = total_co2_recycling + ?,
                        total_co2_avoided = total_co2_avoided + ?,
                        net_co2_emissions = net_co2_emissions + ?,
                        total_waste_diverted = total_waste_diverted + ?,
                        last_updated = ?
                    WHERE id = (SELECT MAX(id) FROM emissions_summary)
                ''', (normal_co2, abs(recycle_co2) if recycle_co2 > 0 else 0, recycle_avoided, 
                      normal_co2 + recycle_co2, recycle_weight, timestamp.strftime('%Y-%m-%d %H:%M:%S')))
                
                print(f"  🧹 Day {day_offset}: Emptied both bins (CO₂ calculated)")
    
    conn.commit()
    conn.close()
    
    print("\n✅ Successfully added 7 days of dummy data!")

if __name__ == "__main__":
    print("=" * 60)
    print("Smart Bin Dashboard - Dummy Data Generator")
    print("=" * 60)
    print("\nThis will add 7 days of sample waste data to your database.")
    
    response = input("\nContinue? (yes/no): ").lower()
    if response in ['yes', 'y']:
        populate_dummy_data()
    else:
        print("Cancelled.")
