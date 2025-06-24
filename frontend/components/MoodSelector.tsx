import React from 'react';
import { Heart, Meh, Frown, Smile, Zap, Bed, HelpCircle } from 'lucide-react';
import { MoodType } from '../types';
import { moodColors, moodEmojis } from '../utils/moodContent';

interface MoodSelectorProps {
  onMoodSelect: (mood: MoodType, intensity: number) => void;
}

const moodOptions: Array<{ mood: MoodType; label: string; icon: React.ReactNode; color: string }> = [
  { mood: 'happy', label: 'Happy', icon: <Smile className="w-6 h-6" />, color: 'text-yellow-600' },
  { mood: 'neutral', label: 'Neutral', icon: <Meh className="w-6 h-6" />, color: 'text-gray-600' },
  { mood: 'anxious', label: 'Anxious', icon: <Zap className="w-6 h-6" />, color: 'text-purple-600' },
  { mood: 'sad', label: 'Sad', icon: <Frown className="w-6 h-6" />, color: 'text-blue-600' },
  { mood: 'angry', label: 'Angry', icon: <Heart className="w-6 h-6" />, color: 'text-red-600' },
  { mood: 'tired', label: 'Tired', icon: <Bed className="w-6 h-6" />, color: 'text-indigo-600' },
  { mood: 'mixed', label: 'Mixed', icon: <HelpCircle className="w-6 h-6" />, color: 'text-teal-600' }
];

export default function MoodSelector({ onMoodSelect }: MoodSelectorProps) {
  const [selectedMood, setSelectedMood] = React.useState<MoodType | null>(null);
  const [intensity, setIntensity] = React.useState(5);

  const handleMoodClick = (mood: MoodType) => {
    setSelectedMood(mood);
  };

  const handleContinue = () => {
    if (selectedMood) {
      onMoodSelect(selectedMood, intensity);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-3xl shadow-xl p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">SafeSpace</h1>
          <p className="text-gray-600">How are you feeling right now?</p>
        </div>

        <div className="grid grid-cols-2 gap-3 mb-6">
          {moodOptions.map(({ mood, label, icon, color }) => (
            <button
              key={mood}
              onClick={() => handleMoodClick(mood)}
              className={`p-4 rounded-2xl border-2 transition-all duration-200 ${
                selectedMood === mood
                  ? 'border-emerald-400 bg-emerald-50 shadow-md scale-105'
                  : 'border-gray-200 hover:border-emerald-200 hover:bg-emerald-25'
              }`}
            >
              <div className="flex flex-col items-center space-y-2">
                <div className={`${color} flex items-center justify-center space-x-1`}>
                  {icon}
                  <span className="text-2xl">{moodEmojis[mood]}</span>
                </div>
                <span className="text-sm font-medium text-gray-700">{label}</span>
              </div>
            </button>
          ))}
        </div>

        {selectedMood && (
          <div className="mb-6 animate-fadeIn">
            <label className="block text-sm font-medium text-gray-700 mb-3">
              How strongly are you feeling this? (1-10)
            </label>
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-500">1</span>
              <input
                type="range"
                min="1"
                max="10"
                value={intensity}
                onChange={(e) => setIntensity(Number(e.target.value))}
                className="flex-1 h-2 bg-gradient-to-r from-emerald-200 to-emerald-400 rounded-lg appearance-none slider"
              />
              <span className="text-sm text-gray-500">10</span>
            </div>
            <div className="text-center mt-2">
              <span className="text-lg font-semibold text-emerald-600">{intensity}</span>
            </div>
          </div>
        )}

        {selectedMood && (
          <button
            onClick={handleContinue}
            className="w-full bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600 text-white font-semibold py-3 px-6 rounded-2xl transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105"
          >
            Continue to Support
          </button>
        )}
      </div>
    </div>
  );
}