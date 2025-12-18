# Smart Trashbin Dashboard with Scope 3 Emissions Tracking

A comprehensive waste management system that tracks bin capacity, waste types, and **Scope 3 carbon emissions** from waste disposal and recycling activities.

## 🌍 Scope 3 Emissions Tracking

This dashboard calculates and displays **Scope 3 indirect greenhouse gas emissions** associated with waste management activities, helping organizations understand their environmental impact and sustainability metrics.

### Emissions Factors

Based on EPA and industry standards:

- **Landfill Emissions**: 0.5 kg CO₂e per kg of waste sent to landfill
- **Recycling Process**: 0.1 kg CO₂e per kg during recycling operations
- **Production Avoided**: 2.0 kg CO₂e avoided per kg of recycled material (from avoided virgin material production)

### Key Metrics Displayed

1. **CO₂ Avoided**: Total carbon emissions prevented through recycling (green/positive impact)
2. **CO₂ from Landfill**: Total emissions from normal waste disposal (red/negative impact)
3. **Waste Diverted**: Total weight of waste diverted from landfills through recycling
4. **Net CO₂ Impact**: Combined impact showing whether operations are carbon-positive or carbon-negative

### Carbon Impact Calculation

- **Normal Waste** (to landfill): Positive emissions (0.5 kg CO₂ per kg waste)
- **Recyclable Waste**: Net negative emissions due to avoided production
  - Process emissions: +0.1 kg CO₂ per kg
  - Avoided production: -2.0 kg CO₂ per kg
  - **Net: -1.9 kg CO₂ per kg** (carbon negative!)

## Features

### 🗑️ Waste Management
- **Dual-bin system** (Normal & Recyclable waste)
- **Real-time capacity monitoring**: Track volume and weight for each waste type
- **Event logging**: Records add and empty operations with brand and product tracking
- **Activity Logs**: View recent trash disposal activities with emissions data
- **Brand & Product Tracking**: Track which brands and products are being disposed

### 📊 Analytics & Statistics
- **Per-bin statistics** with emissions breakdown
- **Activity logs** with CO₂ calculations per event
- **Brand Statistics**: Top 10 brands by item count, with recycle/normal breakdown
- **Comprehensive statistics**: Analyze waste patterns
- **Historical trend tracking**
- **Interactive charts**: Daily collection trends and hourly capacity analysis

### 🌱 Sustainability Insights
- **Carbon footprint visualization**
- **Positive/negative impact indicators**
- **Waste diversion metrics**
- **Real-time sustainability scoring**

### 📷 Camera Feed Integration
- **Live camera feed**: View real-time camera stream from external devices
- **Base64 image transmission**: External cameras can send images via API
- **Auto-refresh management**: Pauses dashboard refresh during camera viewing

### 🔌 API & Integration
- **REST API**: Multiple endpoints for IoT device integration
- **Simplified JSON API**: Easy integration for smart bins with minimal data
- **Auto-refresh**: Dashboard updates every 30 seconds
- **Collapsible sections**: Mobile-optimized UI with expandable content

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open your browser and navigate to:
```
http://localhost:5000
```

## API Endpoints

### Add Trash Entry (Detailed)
**POST** `/api/trash`

Add a new trash entry with full details.

```json
{
  "waste_type": "normal",
  "volume": 5.5,
  "weight": 2.3,
  "brand": "Coca-Cola",
  "product": "Soda Can"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Normal waste added successfully",
  "current_status": {
    "normal_volume": 15.5,
    "normal_weight": 8.3,
    "recycle_volume": 10.2,
    "recycle_weight": 5.1
  }
}
```

### Add Item (Simplified JSON)
**POST** `/api/add-item`

Simplified API endpoint for smart bins with minimal data format.

```json
{
  "recyclable": true,
  "weight_in_gram": 250,
  "product_brand": "Coca-Cola",
  "product_name": "Soda Can"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Recyclable item added successfully",
  "item": {
    "product_name": "Soda Can",
    "product_brand": "Coca-Cola",
    "weight_kg": 0.25,
    "recyclable": true
  },
  "current_status": {
    "normal_weight_kg": 8.3,
    "recycle_weight_kg": 5.35
  }
}
```

### Get Current Status
**GET** `/api/status`

Get the current status of both bins.

**Response:**
```json
{
  "normal_volume": 15.5,
  "normal_weight": 8.3,
  "recycle_volume": 10.2,
  "recycle_weight": 5.1,
  "normal_capacity": 100,
  "recycle_capacity": 100,
  "last_updated": "2025-12-17 10:30:45"
}
```

### Camera Feed
**POST** `/api/camera-feed`

Send a camera image (base64 encoded) to be displayed on the dashboard.

```json
{
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
}
```

**GET** `/api/camera-feed`

Get the latest camera image.

**Response:**
```json
{
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
  "timestamp": "2025-12-18T10:30:45.123456"
}
```

### Reset Bin
**POST** `/api/reset`

Reset/empty one or both bins. **This triggers Scope 3 emissions calculations.**

```json
{
  "waste_type": "both"
}
```

**Note**: Emissions are calculated ONLY when bins are emptied, not when waste is added.

## Environmental Impact

By tracking Scope 3 emissions, this system helps organizations:
- ✅ Monitor their carbon footprint from waste operations
- ✅ Identify opportunities to increase recycling rates
- ✅ Demonstrate sustainability commitments with data
- ✅ Meet ESG reporting requirements
- ✅ Make data-driven waste management decisions

## Usage Example

### Scenario: Emptying Bins
When a bin is emptied, the system calculates:

**Normal Waste Bin (10 kg)**
- Landfill emissions: 10 kg × 0.5 = **5.0 kg CO₂** ❌

**Recyclable Bin (10 kg)**
- Process emissions: 10 kg × 0.1 = 1.0 kg CO₂
- Avoided emissions: 10 kg × 2.0 = 20.0 kg CO₂
- Net impact: **-19.0 kg CO₂** ✅ (Carbon negative!)

### Dashboard View
The dashboard displays these calculations in real-time with:
- Color-coded cards (green for avoided, red for emitted)
- Net carbon impact with positive/negative indicators
- Historical trends and cumulative totals

## Example Usage

### Using curl

Add item (simplified format):
```bash
curl -X POST http://localhost:5000/api/add-item \
  -H "Content-Type: application/json" \
  -d '{"recyclable":true,"weight_in_gram":250,"product_brand":"Coca-Cola","product_name":"Soda Can"}'
```

Add normal waste:
```bash
curl -X POST http://localhost:5000/api/trash \
  -H "Content-Type: application/json" \
  -d '{"waste_type":"normal","volume":3.5,"weight":1.2,"brand":"Pepsi","product":"Bottle"}'
```

Add recyclable waste:
```bash
curl -X POST http://localhost:5000/api/trash \
  -H "Content-Type: application/json" \
  -d '{"waste_type":"recycle","volume":2.8,"weight":0.5,"brand":"Coca-Cola","product":"Can"}'
```

Send camera image:
```bash
curl -X POST http://localhost:5000/api/camera-feed \
  -H "Content-Type: application/json" \
  -d '{"image":"data:image/jpeg;base64,/9j/4AAQ..."}'
```

Get status:
```bash
curl http://localhost:5000/api/status
```

Reset bins:
```bash
curl -X POST http://localhost:5000/api/reset \
  -H "Content-Type: application/json" \
  -d '{"waste_type":"both"}'
```

### Using Python

```python
import requests

# Add item (simplified)
response = requests.post('http://localhost:5000/api/add-item', 
    json={
        'recyclable': True,
        'weight_in_gram': 250,
        'product_brand': 'Coca-Cola',
        'product_name': 'Soda Can'
    })
print(response.json())

# Add trash (detailed)
response = requests.post('http://localhost:5000/api/trash', 
    json={
        'waste_type': 'normal',
        'volume': 3.5,
        'weight': 1.2,
        'brand': 'Pepsi',
        'product': 'Bottle'
    })
print(response.json())

# Get status
response = requests.get('http://localhost:5000/api/status')
print(response.json())
```

### Camera Client Example

Use the included `camera_client_example.py` to send images from external cameras:

```bash
python camera_client_example.py path/to/image.jpg
```

## Database Schema

The application uses SQLite with three tables:

### trashbin_status
- `id`: Primary key
- `normal_volume`: Current normal waste volume (liters)
- `normal_weight`: Current normal waste weight (kg)
- `recycle_volume`: Current recyclable waste volume (liters)
- `recycle_weight`: Current recyclable waste weight (kg)
- `normal_capacity`: Maximum capacity for normal waste (default: 100L)
- `recycle_capacity`: Maximum capacity for recyclable waste (default: 100L)
- `last_updated`: Timestamp of last update

### trash_logs
- `id`: Primary key
- `waste_type`: Type of waste ("normal" or "recycle")
- `volume`: Volume of waste added (liters)
- `weight`: Weight of waste added (kg)
- `brand`: Brand name of the product (optional)
- `product`: Product name/description (optional)
- `event_type`: Event type ("add" or "empty")
- `co2_emissions`: CO₂ emissions in kg (calculated on empty events)
- `timestamp`: When the event occurred

### emissions_summary
- `id`: Primary key
- `total_co2_landfill`: Total CO₂ emissions from landfill (kg)
- `total_co2_recycling`: Process emissions from recycling (kg)
- `total_co2_avoided`: Emissions avoided by recycling (kg)
- `net_co2_emissions`: Net carbon impact (kg)
- `total_waste_diverted`: Total weight diverted from landfill (kg)
- `last_updated`: Timestamp of last update

## Future Enhancements

- [x] Advanced analytics charts (Chart.js integration)
- [x] Brand and product tracking
- [x] Camera feed integration for visual monitoring
- [x] Mobile-optimized collapsible UI
- [ ] Export reports (PDF/CSV) for ESG reporting
- [ ] Multi-location support for facility-wide tracking
- [ ] Custom emissions factors per waste type
- [ ] Mobile app integration
- [ ] Real-time IoT sensor integration with MQTT
- [ ] Carbon offset recommendations
- [ ] Benchmarking against industry standards
- [ ] Machine learning for waste classification
- [ ] QR code scanning for product identification

## License

MIT License - Feel free to use for sustainability initiatives!
