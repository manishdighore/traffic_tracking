'use client'

import { useEffect, useRef, useState, useCallback } from 'react'
import { Camera, CameraOff, Loader2, AlertCircle, Car, Upload, Video } from 'lucide-react'
import axios from 'axios'

const WS_URL = 'ws://localhost:8000/ws/video'
const API_URL = 'http://localhost:8000'

interface Detection {
  bbox: number[]
  center: number[]
  confidence: number
  class_name: string
  color: string
  speed: number | null
  direction: string | null
  vehicle_id: number
}

interface WebSocketMessage {
  type: string
  frame?: string
  detections?: Detection[]
  count?: number
  frame_number?: number
  message?: string
}

export function VideoFeed() {
  const [isConnected, setIsConnected] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [detections, setDetections] = useState<Detection[]>([])
  const [vehicleCount, setVehicleCount] = useState(0)
  const [frameNumber, setFrameNumber] = useState(0)
  const [fps, setFps] = useState(0)
  const [videoSource, setVideoSource] = useState<'camera' | 'file'>('camera')
  const [uploadProgress, setUploadProgress] = useState(0)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [roiPosition, setRoiPosition] = useState(400)  // ROI line Y position
  
  const wsRef = useRef<WebSocket | null>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const fpsCounterRef = useRef({ frames: 0, lastTime: Date.now() })
  const fileInputRef = useRef<HTMLInputElement>(null)

  const connectWebSocket = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return
    }

    setIsLoading(true)
    setError(null)

    const ws = new WebSocket(WS_URL)
    wsRef.current = ws

    ws.onopen = () => {
      console.log('WebSocket connected')
      setIsConnected(true)
      setIsLoading(false)
      
      // Send configuration
      ws.send(JSON.stringify({
        source: 0,  // 0 for webcam
        roi_y: roiPosition
      }))
    }

    ws.onmessage = (event) => {
      try {
        const data: WebSocketMessage = JSON.parse(event.data)
        
        if (data.type === 'error') {
          setError(data.message || 'Unknown error')
          setIsLoading(false)
          return
        }

        if (data.type === 'frame' && data.frame) {
          // Update detections
          setDetections(data.detections || [])
          setVehicleCount(data.count || 0)
          setFrameNumber(data.frame_number || 0)
          
          // Calculate FPS
          fpsCounterRef.current.frames++
          const now = Date.now()
          const elapsed = now - fpsCounterRef.current.lastTime
          if (elapsed >= 1000) {
            setFps(Math.round((fpsCounterRef.current.frames * 1000) / elapsed))
            fpsCounterRef.current.frames = 0
            fpsCounterRef.current.lastTime = now
          }
          
          // Draw frame on canvas
          const canvas = canvasRef.current
          if (canvas) {
            const ctx = canvas.getContext('2d')
            if (ctx) {
              const img = new Image()
              img.onload = () => {
                canvas.width = img.width
                canvas.height = img.height
                ctx.drawImage(img, 0, 0)
              }
              img.src = `data:image/jpeg;base64,${data.frame}`
            }
          }
        }
      } catch (err) {
        console.error('Error parsing WebSocket message:', err)
      }
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      setError('Connection error occurred')
      setIsLoading(false)
    }

    ws.onclose = () => {
      console.log('WebSocket disconnected')
      setIsConnected(false)
      setIsLoading(false)
    }
  }, [])

  const disconnectWebSocket = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
      setIsConnected(false)
      setDetections([])
    }
  }, [])

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setSelectedFile(file)
      setVideoSource('file')
    }
  }

  const handleVideoUpload = async () => {
    if (!selectedFile) {
      setError('Please select a video file first')
      return
    }

    setIsLoading(true)
    setError(null)
    setUploadProgress(0)

    const formData = new FormData()
    formData.append('file', selectedFile)

    try {
      const response = await axios.post(`${API_URL}/api/upload-video`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
            setUploadProgress(progress)
          }
        },
      })

      if (response.data.status === 'success') {
        // Connect WebSocket and send video path once connected
        const ws = new WebSocket(WS_URL)
        wsRef.current = ws
        
        ws.onopen = () => {
          console.log('WebSocket connected for video processing')
          setIsConnected(true)
          setIsLoading(false)
          // Send video file path and ROI position to backend
          ws.send(JSON.stringify({ 
            source: response.data.file_path,
            roi_y: roiPosition
          }))
        }
        
        ws.onmessage = (event) => {
          try {
            const data: WebSocketMessage = JSON.parse(event.data)
            
            if (data.type === 'error') {
              setError(data.message || 'Error processing video')
              return
            }
            
            if (data.type === 'frame' && data.frame) {
              setDetections(data.detections || [])
              setVehicleCount(data.count || 0)
              setFrameNumber(data.frame_number || 0)
              
              // Calculate FPS
              fpsCounterRef.current.frames++
              const now = Date.now()
              const elapsed = now - fpsCounterRef.current.lastTime
              if (elapsed >= 1000) {
                setFps(Math.round((fpsCounterRef.current.frames * 1000) / elapsed))
                fpsCounterRef.current.frames = 0
                fpsCounterRef.current.lastTime = now
              }
              
              // Draw frame on canvas
              const canvas = canvasRef.current
              if (canvas) {
                const ctx = canvas.getContext('2d')
                if (ctx) {
                  const img = new Image()
                  img.onload = () => {
                    canvas.width = img.width
                    canvas.height = img.height
                    ctx.drawImage(img, 0, 0)
                  }
                  img.src = `data:image/jpeg;base64,${data.frame}`
                }
              }
            }
          } catch (err) {
            console.error('Error parsing WebSocket message:', err)
          }
        }
        
        ws.onerror = (error) => {
          console.error('WebSocket error:', error)
          setError('Connection error occurred')
          setIsLoading(false)
        }
        
        ws.onclose = () => {
          console.log('WebSocket disconnected')
          setIsConnected(false)
          setIsLoading(false)
        }
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to upload video')
    } finally {
      setIsLoading(false)
      setUploadProgress(0)
    }
  }

  const startCamera = () => {
    setVideoSource('camera')
    setSelectedFile(null)
    connectWebSocket()
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ 
        source: 0,  // 0 for webcam
        roi_y: roiPosition
      }))
    }
  }

  useEffect(() => {
    return () => {
      disconnectWebSocket()
    }
  }, [disconnectWebSocket])

  return (
    <div className="space-y-6">
      {/* Controls */}
      <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-6 border border-gray-700">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-white">Video Feed</h2>
          
          {isConnected && (
            <div className="flex items-center gap-4 text-sm">
              <div className="text-gray-400">
                FPS: <span className="text-white font-mono">{fps}</span>
              </div>
              <div className="text-gray-400">
                Frame: <span className="text-white font-mono">{frameNumber}</span>
              </div>
            </div>
          )}
        </div>

        {/* ROI Position Control */}
        {!isConnected && (
          <div className="mb-4 p-4 rounded-lg bg-blue-500/10 border border-blue-500/20">
            <label className="block text-sm font-medium text-white mb-3">
              ROI Line Position (Y): <span className="text-blue-400 font-mono">{roiPosition}px</span>
            </label>
            <input
              type="range"
              min="100"
              max="800"
              step="10"
              value={roiPosition}
              onChange={(e) => setRoiPosition(parseInt(e.target.value))}
              className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
            />
            <p className="text-xs text-gray-400 mt-2">
              Vehicles crossing this line will be counted. Adjust based on your video resolution.
            </p>
          </div>
        )}

        {/* Source Selection */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          {/* Camera Option */}
          <div className="flex flex-col gap-2">
            <button
              onClick={startCamera}
              disabled={isLoading || isConnected}
              className="flex items-center justify-center gap-2 px-6 py-3 rounded-lg font-medium transition-all bg-primary-600 hover:bg-primary-700 text-white disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Camera className="w-5 h-5" />
              Start Camera
            </button>
          </div>

          {/* Video Upload Option */}
          <div className="flex flex-col gap-2">
            <input
              ref={fileInputRef}
              type="file"
              accept="video/*"
              onChange={handleFileSelect}
              className="hidden"
            />
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={isLoading || isConnected}
              className="flex items-center justify-center gap-2 px-6 py-3 rounded-lg font-medium transition-all bg-green-600 hover:bg-green-700 text-white disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Upload className="w-5 h-5" />
              Select Video File
            </button>
          </div>
        </div>

        {/* Selected File Info */}
        {selectedFile && !isConnected && (
          <div className="mb-4 p-4 rounded-lg bg-blue-500/10 border border-blue-500/20">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Video className="w-5 h-5 text-blue-400" />
                <div>
                  <p className="text-sm font-medium text-white">{selectedFile.name}</p>
                  <p className="text-xs text-gray-400">
                    {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
              </div>
              <button
                onClick={handleVideoUpload}
                disabled={isLoading}
                className="flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all bg-blue-600 hover:bg-blue-700 text-white disabled:opacity-50"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Uploading... {uploadProgress}%
                  </>
                ) : (
                  <>
                    <Video className="w-4 h-4" />
                    Process Video
                  </>
                )}
              </button>
            </div>
          </div>
        )}

        {/* Stop Button */}
        {isConnected && (
          <div className="mb-4">
            <button
              onClick={disconnectWebSocket}
              className="flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all bg-red-600 hover:bg-red-700 text-white w-full justify-center"
            >
              <CameraOff className="w-4 h-4" />
              Stop
            </button>
          </div>
        )}

        {error && (
          <div className="mb-4 flex items-center gap-2 p-4 rounded-lg bg-red-900/20 border border-red-500/20 text-red-400">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Video Canvas */}
        <div className="relative aspect-video bg-gray-900 rounded-lg overflow-hidden">
          {!isConnected && !isLoading && (
            <div className="absolute inset-0 flex flex-col items-center justify-center text-gray-400">
              <Camera className="w-16 h-16 mb-4 opacity-30" />
              <p className="text-sm">Click "Start Camera" to begin</p>
            </div>
          )}
          
          <canvas
            ref={canvasRef}
            className="w-full h-full object-contain"
          />
          
          {/* Overlay Stats */}
          {isConnected && (
            <div className="absolute top-4 left-4 bg-black/60 backdrop-blur-sm px-4 py-2 rounded-lg">
              <div className="text-sm text-gray-300">
                Total Vehicles: <span className="text-green-400 font-bold text-lg ml-2">{vehicleCount}</span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Current Detections */}
      {isConnected && detections.length > 0 && (
        <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-6 border border-gray-700">
          <h3 className="text-lg font-bold text-white mb-4">
            Current Detections ({detections.length})
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {detections.map((detection, index) => (
              <div
                key={index}
                className="bg-gray-900/50 rounded-lg p-4 border border-gray-700 hover:border-primary-500 transition-colors"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Car className="w-4 h-4 text-primary-400" />
                    <span className="font-semibold text-white">
                      {detection.class_name}
                    </span>
                  </div>
                  <span className="text-xs text-gray-400">
                    #{detection.vehicle_id}
                  </span>
                </div>
                
                <div className="space-y-1 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Color:</span>
                    <span className="text-white capitalize">{detection.color}</span>
                  </div>
                  
                  {detection.speed !== null && (
                    <div className="flex justify-between">
                      <span className="text-gray-400">Speed:</span>
                      <span className="text-green-400 font-mono">
                        {detection.speed} km/h
                      </span>
                    </div>
                  )}
                  
                  {detection.direction && (
                    <div className="flex justify-between">
                      <span className="text-gray-400">Direction:</span>
                      <span className="text-blue-400 capitalize">
                        {detection.direction}
                      </span>
                    </div>
                  )}
                  
                  <div className="flex justify-between">
                    <span className="text-gray-400">Confidence:</span>
                    <span className="text-white">
                      {(detection.confidence * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
