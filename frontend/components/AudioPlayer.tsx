import React, { useState } from 'react';
import { ArrowLeft, Play, Pause, Volume2, VolumeX } from 'lucide-react';
import { MoodType } from '../types';
import { moodColors } from '../utils/moodContent';

interface AudioPlayerProps {
  mood: MoodType;
  onBack: () => void;
}

const audioOptions: Record<MoodType, Array<{ title: string; description: string; duration: string }>> = {
  happy: [
    { title: 'Uplifting Music', description: 'Energizing melodies to match your joy', duration: '10:00' },
    { title: 'Nature Celebration', description: 'Birds singing and gentle streams', duration: '15:00' },
    { title: 'Positive Affirmations', description: 'Encouraging words for your happy day', duration: '8:00' }
  ],
  neutral: [
    { title: 'Gentle Ambience', description: 'Soft background sounds for reflection', duration: '20:00' },
    { title: 'Piano Meditation', description: 'Peaceful piano for contemplation', duration: '12:00' },
    { title: 'White Noise', description: 'Consistent, calming background sound', duration: '30:00' }
  ],
  anxious: [
    { title: 'Calming Rain', description: 'Gentle rainfall to soothe anxiety', duration: '25:00' },
    { title: 'Ocean Waves', description: 'Rhythmic waves for deep relaxation', duration: '20:00' },
    { title: 'Anxiety Relief', description: 'Guided breathing with soft music', duration: '15:00' }
  ],
  sad: [
    { title: 'Comfort Music', description: 'Gentle melodies for difficult times', duration: '18:00' },
    { title: 'Healing Sounds', description: 'Soft tones for emotional healing', duration: '22:00' },
    { title: 'Compassion Audio', description: 'Warm, supportive soundscape', duration: '16:00' }
  ],
  angry: [
    { title: 'Release Beats', description: 'Rhythmic sounds for energy release', duration: '12:00' },
    { title: 'Cooling Rain', description: 'Rain sounds to cool heated emotions', duration: '20:00' },
    { title: 'Grounding Tones', description: 'Deep, steady sounds for centering', duration: '14:00' }
  ],
  tired: [
    { title: 'Sleep Sounds', description: 'Gentle sounds for rest and recovery', duration: '45:00' },
    { title: 'Deep Rest', description: 'Ultra-calming audio for exhaustion', duration: '35:00' },
    { title: 'Restorative Tones', description: 'Healing frequencies for tired souls', duration: '28:00' }
  ],
  mixed: [
    { title: 'Emotional Balance', description: 'Mixed tones for complex feelings', duration: '18:00' },
    { title: 'Reflection Music', description: 'Contemplative sounds for processing', duration: '20:00' },
    { title: 'Gentle Support', description: 'Versatile audio for any emotion', duration: '15:00' }
  ]
};

export default function AudioPlayer({ mood, onBack }: AudioPlayerProps) {
  const [selectedTrack, setSelectedTrack] = useState<number | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [volume, setVolume] = useState(70);
  const [isMuted, setIsMuted] = useState(false);
  const [progress, setProgress] = useState(0);

  const tracks = audioOptions[mood];

  // Simulate audio playback
  React.useEffect(() => {
    if (isPlaying && selectedTrack !== null) {
      const interval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 100) {
            setIsPlaying(false);
            return 0;
          }
          return prev + 0.5;
        });
      }, 1000);
      return () => clearInterval(interval);
    }
  }, [isPlaying, selectedTrack]);

  const handlePlayPause = (trackIndex: number) => {
    if (selectedTrack === trackIndex) {
      setIsPlaying(!isPlaying);
    } else {
      setSelectedTrack(trackIndex);
      setIsPlaying(true);
      setProgress(0);
    }
  };

  const formatTime = (percentage: number, duration: string) => {
    const totalMinutes = parseInt(duration.split(':')[0]);
    const currentMinutes = Math.floor((percentage / 100) * totalMinutes);
    const currentSeconds = Math.floor(((percentage / 100) * totalMinutes * 60) % 60);
    return `${currentMinutes}:${currentSeconds.toString().padStart(2, '0')}`;
  };

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
          <h1 className="text-xl font-semibold text-gray-800">Calming Audio</h1>
          <div className="w-9"></div>
        </div>

        <div className="bg-white/90 backdrop-blur-sm rounded-2xl p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4 text-center">
            Audio for {mood} moments
          </h2>
          <p className="text-gray-600 text-sm text-center">
            Choose sounds that resonate with how you're feeling right now.
          </p>
        </div>

        <div className="space-y-3 mb-6">
          {tracks.map((track, index) => (
            <div
              key={index}
              className={`bg-white/90 backdrop-blur-sm rounded-2xl p-4 transition-all ${
                selectedTrack === index ? 'ring-2 ring-emerald-400 bg-white' : ''
              }`}
            >
              <div className="flex items-center space-x-4">
                <button
                  onClick={() => handlePlayPause(index)}
                  className={`p-3 rounded-full transition-colors ${
                    selectedTrack === index && isPlaying
                      ? 'bg-emerald-500 hover:bg-emerald-600'
                      : 'bg-emerald-400 hover:bg-emerald-500'
                  }`}
                >
                  {selectedTrack === index && isPlaying ? (
                    <Pause className="w-5 h-5 text-white" />
                  ) : (
                    <Play className="w-5 h-5 text-white" />
                  )}
                </button>

                <div className="flex-1">
                  <h3 className="font-semibold text-gray-800">{track.title}</h3>
                  <p className="text-sm text-gray-600">{track.description}</p>
                  <p className="text-xs text-emerald-600 mt-1">{track.duration}</p>
                </div>
              </div>

              {selectedTrack === index && (
                <div className="mt-4 animate-fadeIn">
                  <div className="flex items-center space-x-2 mb-2">
                    <span className="text-xs text-gray-500">
                      {formatTime(progress, track.duration)}
                    </span>
                    <div className="flex-1 bg-gray-200 rounded-full h-1">
                      <div
                        className="bg-emerald-400 h-1 rounded-full transition-all duration-300"
                        style={{ width: `${progress}%` }}
                      />
                    </div>
                    <span className="text-xs text-gray-500">{track.duration}</span>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>

        {selectedTrack !== null && (
          <div className="bg-white/90 backdrop-blur-sm rounded-2xl p-4 animate-fadeIn">
            <div className="flex items-center justify-between">
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
            <div className="flex items-center space-x-2 mt-2">
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
        )}

        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600">
            🎧 Use headphones for the best experience
          </p>
        </div>
      </div>
    </div>
  );
}