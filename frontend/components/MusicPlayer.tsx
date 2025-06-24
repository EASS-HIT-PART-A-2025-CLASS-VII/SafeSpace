import { useState, useEffect } from 'react';
import { ArrowLeft, Play, Pause, SkipForward, SkipBack, Volume2, VolumeX, Loader } from 'lucide-react';
import { MoodType } from '../types';
import { moodColors } from '../utils/moodContent';

interface Track {
  id: string;
  title: string;
  artist: string;
  duration: number;
  url: string;
  preview_url?: string;
  image_url?: string;
}

interface Playlist {
  id: string;
  name: string;
  description: string;
  tracks: Track[];
  total_duration: number;
  mood_type: MoodType;
  intensity: number;
}

interface MusicPlayerProps {
  mood: MoodType;
  intensity: number;
  onBack: () => void;
}

export default function MusicPlayer({ mood, intensity, onBack }: MusicPlayerProps) {
  const [playlist, setPlaylist] = useState<Playlist | null>(null);
  const [currentTrack, setCurrentTrack] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [volume, setVolume] = useState(70);
  const [isMuted, setIsMuted] = useState(false);
  const [progress, setProgress] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    generatePlaylist();
  }, [mood, intensity]);

  const generatePlaylist = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Get auth token from localStorage (you'll need to implement auth)
      const token = localStorage.getItem('auth_token');
      
      const response = await fetch('/api/music/playlist', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          mood_type: mood,
          intensity: intensity,
          source: 'spotify',
          duration_minutes: 30
        })
      });

      if (!response.ok) {
        throw new Error('Failed to generate playlist');
      }

      const playlistData = await response.json();
      setPlaylist(playlistData);
      
      if (playlistData.tracks.length > 0) {
        setCurrentTrack(0);
      }
    } catch (err) {
      setError('Unable to generate playlist. Please try again.');
      console.error('Playlist generation error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Simulate audio playback
  useEffect(() => {
    if (isPlaying && playlist?.tracks[currentTrack]) {
      const interval = setInterval(() => {
        setProgress(prev => {
          const trackDuration = playlist.tracks[currentTrack].duration;
          if (prev >= trackDuration) {
            // Auto-advance to next track
            if (currentTrack < playlist.tracks.length - 1) {
              setCurrentTrack(prev => prev + 1);
              return 0;
            } else {
              setIsPlaying(false);
              return 0;
            }
          }
          return prev + 1;
        });
      }, 1000);
      return () => clearInterval(interval);
    }
  }, [isPlaying, currentTrack, playlist]);

  const handlePlayPause = () => {
    setIsPlaying(!isPlaying);
  };

  const handleNextTrack = () => {
    if (playlist && currentTrack < playlist.tracks.length - 1) {
      setCurrentTrack(prev => prev + 1);
      setProgress(0);
    }
  };

  const handlePrevTrack = () => {
    if (currentTrack > 0) {
      setCurrentTrack(prev => prev - 1);
      setProgress(0);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const currentTrackData = playlist?.tracks[currentTrack];

  if (isLoading) {
    return (
      <div className={`min-h-screen bg-gradient-to-br ${moodColors[mood]} p-4 flex items-center justify-center`}>
        <div className="bg-white/90 backdrop-blur-sm rounded-3xl p-8 text-center">
          <Loader className="w-12 h-12 animate-spin text-emerald-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-800 mb-2">Creating Your Playlist</h2>
          <p className="text-gray-600">AI is curating the perfect music for your {mood} mood...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`min-h-screen bg-gradient-to-br ${moodColors[mood]} p-4 flex items-center justify-center`}>
        <div className="bg-white/90 backdrop-blur-sm rounded-3xl p-8 text-center">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h2 className="text-xl font-semibold text-gray-800 mb-2">Oops!</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={generatePlaylist}
            className="bg-emerald-500 hover:bg-emerald-600 text-white px-6 py-2 rounded-xl font-medium transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={`min-h-screen bg-gradient-to-br ${moodColors[mood]} p-4`}>
      <div className="max-w-md mx-auto">
        <div className="flex items-center justify-between mb-6">
          <button
            onClick={onBack}
            className="p-2 rounded-full bg-white/80 hover:bg-white transition-colors"
          >
            <ArrowLeft className="w-5 h-5 text-gray-600" />
          </button>
          <h1 className="text-xl font-semibold text-gray-800">AI Music</h1>
          <div className="w-9"></div>
        </div>

        {playlist && (
          <>
            {/* Playlist Info */}
            <div className="bg-white/90 backdrop-blur-sm rounded-2xl p-6 mb-6">
              <h2 className="text-lg font-semibold text-gray-800 mb-2">{playlist.name}</h2>
              <p className="text-gray-600 text-sm mb-4">{playlist.description}</p>
              <div className="flex justify-between text-sm text-gray-500">
                <span>{playlist.tracks.length} tracks</span>
                <span>{formatTime(playlist.total_duration)}</span>
              </div>
            </div>

            {/* Current Track */}
            {currentTrackData && (
              <div className="bg-white/90 backdrop-blur-sm rounded-2xl p-6 mb-6">
                <div className="flex items-center space-x-4 mb-4">
                  {currentTrackData.image_url && (
                    <img
                      src={currentTrackData.image_url}
                      alt={currentTrackData.title}
                      className="w-16 h-16 rounded-xl object-cover"
                    />
                  )}
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-800 truncate">{currentTrackData.title}</h3>
                    <p className="text-gray-600 text-sm truncate">{currentTrackData.artist}</p>
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="mb-4">
                  <div className="flex justify-between text-xs text-gray-500 mb-1">
                    <span>{formatTime(progress)}</span>
                    <span>{formatTime(currentTrackData.duration)}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-emerald-400 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${(progress / currentTrackData.duration) * 100}%` }}
                    />
                  </div>
                </div>

                {/* Controls */}
                <div className="flex items-center justify-center space-x-6">
                  <button
                    onClick={handlePrevTrack}
                    disabled={currentTrack === 0}
                    className="p-2 rounded-full bg-gray-100 hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    <SkipBack className="w-5 h-5 text-gray-600" />
                  </button>

                  <button
                    onClick={handlePlayPause}
                    className="p-4 rounded-full bg-emerald-500 hover:bg-emerald-600 text-white transition-colors"
                  >
                    {isPlaying ? (
                      <Pause className="w-6 h-6" />
                    ) : (
                      <Play className="w-6 h-6" />
                    )}
                  </button>

                  <button
                    onClick={handleNextTrack}
                    disabled={currentTrack === playlist.tracks.length - 1}
                    className="p-2 rounded-full bg-gray-100 hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    <SkipForward className="w-5 h-5 text-gray-600" />
                  </button>
                </div>
              </div>
            )}

            {/* Volume Control */}
            <div className="bg-white/90 backdrop-blur-sm rounded-2xl p-4 mb-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">Volume</span>
                <button
                  onClick={() => setIsMuted(!isMuted)}
                  className="p-1 text-gray-600 hover:text-gray-800"
                >
                  {isMuted || volume === 0 ? (
                    <VolumeX className="w-5 h-5" />
                  ) : (
                    <Volume2 className="w-5 h-5" />
                  )}
                </button>
              </div>
              <div className="flex items-center space-x-2">
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={isMuted ? 0 : volume}
                  onChange={(e) => {
                    setVolume(Number(e.target.value));
                    if (Number(e.target.value) > 0) setIsMuted(false);
                  }}
                  className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none slider"
                />
                <span className="text-sm text-gray-600 w-8">
                  {isMuted ? 0 : volume}
                </span>
              </div>
            </div>

            {/* Track List */}
            <div className="bg-white/90 backdrop-blur-sm rounded-2xl p-4">
              <h3 className="font-semibold text-gray-800 mb-3">Playlist</h3>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {playlist.tracks.map((track, index) => (
                  <button
                    key={track.id}
                    onClick={() => {
                      setCurrentTrack(index);
                      setProgress(0);
                    }}
                    className={`w-full text-left p-3 rounded-xl transition-colors ${
                      index === currentTrack
                        ? 'bg-emerald-100 border border-emerald-200'
                        : 'hover:bg-gray-50'
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm ${
                        index === currentTrack
                          ? 'bg-emerald-500 text-white'
                          : 'bg-gray-200 text-gray-600'
                      }`}>
                        {index + 1}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-gray-800 truncate">{track.title}</p>
                        <p className="text-sm text-gray-600 truncate">{track.artist}</p>
                      </div>
                      <span className="text-xs text-gray-500">{formatTime(track.duration)}</span>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}