# Car Tracking Frontend

Modern Next.js 14 frontend for real-time car tracking and analytics.

## Features

- 🎥 **Real-time Video Feed** - Live camera stream with WebSocket
- 🎯 **Detection Visualization** - Real-time bounding boxes and labels
- 📊 **Interactive Dashboard** - Charts and analytics
- 📜 **Vehicle History** - Complete tracking history with filters
- 🎨 **Beautiful UI** - Modern, responsive design with Tailwind CSS
- ⚡ **Fast & Optimized** - Built with Next.js 14 and React Query

## Installation

### Prerequisites

- Node.js 18+
- npm or yarn
- Backend running on `http://localhost:8000`

### Setup

1. **Install dependencies**:
```bash
cd frontend
npm install
```

2. **Start development server**:
```bash
npm run dev
```

3. **Open browser**:
Navigate to `http://localhost:3000`

## Usage

### Live Feed Tab
- Click "Start Camera" to begin real-time tracking
- View detections with bounding boxes, colors, speeds, and directions
- Monitor FPS and frame count
- Stop camera when done

### Dashboard Tab
- View overall statistics
- Analyze vehicle type distribution
- See color breakdown
- Monitor average speeds
- Interactive charts with real-time updates

### History Tab
- Browse all detected vehicles
- View detailed information for each detection
- Delete individual records
- Clear all data

## Configuration

### API Endpoint

Edit in component files:
```typescript
const API_URL = 'http://localhost:8000'
const WS_URL = 'ws://localhost:8000/ws/video'
```

### Update Intervals

Modify in Dashboard and History components:
```typescript
refetchInterval: 5000, // 5 seconds
```

## Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx          # Root layout
│   │   ├── page.tsx             # Home page with tabs
│   │   ├── providers.tsx        # React Query provider
│   │   └── globals.css          # Global styles
│   └── components/
│       ├── Header.tsx           # App header
│       ├── VideoFeed.tsx        # Live video feed
│       ├── Dashboard.tsx        # Analytics dashboard
│       └── VehicleHistory.tsx   # Vehicle history
├── public/                      # Static assets
├── package.json                 # Dependencies
├── tsconfig.json                # TypeScript config
├── tailwind.config.js           # Tailwind config
└── next.config.js               # Next.js config
```

## Components

### VideoFeed
Real-time video streaming with WebSocket connection. Displays:
- Live camera feed
- Bounding boxes for detected vehicles
- Vehicle information overlays
- FPS counter
- Total vehicle count

### Dashboard
Analytics and statistics dashboard featuring:
- Stat cards (total vehicles, types, colors, avg speed)
- Bar chart for vehicle types
- Pie chart for color distribution
- Detailed breakdowns

### VehicleHistory
Complete history of detected vehicles with:
- Grid layout of vehicle cards
- Detailed information per vehicle
- Delete individual records
- Clear all data functionality

## Styling

Built with Tailwind CSS featuring:
- Dark theme with gradient backgrounds
- Glass morphism effects
- Smooth animations
- Responsive design
- Custom color palette

## API Integration

Uses React Query for:
- Automatic refetching
- Caching
- Loading states
- Error handling

WebSocket for:
- Real-time video streaming
- Live detection updates
- Low-latency communication

## Performance Tips

1. **Optimize Video Quality**: Adjust backend frame encoding quality
2. **Reduce Update Frequency**: Increase `refetchInterval` for slower connections
3. **Limit History**: Use pagination for large datasets
4. **Browser Performance**: Use Chrome or Edge for best WebSocket performance

## Development

### Adding New Components

1. Create component in `src/components/`
2. Import in `src/app/page.tsx`
3. Add to tab navigation

### Modifying Styles

- Global styles: `src/app/globals.css`
- Tailwind config: `tailwind.config.js`
- Component-specific: Use Tailwind utility classes

### Type Safety

TypeScript interfaces for:
- Vehicle data
- API responses
- WebSocket messages
- Component props

## Building for Production

```bash
# Build the app
npm run build

# Start production server
npm start
```

## Troubleshooting

### WebSocket Connection Fails
- Ensure backend is running on port 8000
- Check CORS settings in backend
- Verify firewall isn't blocking WebSocket connections

### Charts Not Displaying
- Ensure recharts is installed
- Check browser console for errors
- Verify data format from API

### Slow Performance
- Reduce video quality in backend
- Increase refetch intervals
- Check network bandwidth
- Use production build

## Browser Support

- Chrome/Edge: Full support ✅
- Firefox: Full support ✅
- Safari: Full support ✅
- Mobile: Responsive design ✅

## License

MIT License - See root LICENSE file
