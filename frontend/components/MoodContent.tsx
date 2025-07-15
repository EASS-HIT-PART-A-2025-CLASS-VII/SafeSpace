import React from 'react';
import { ArrowLeft, Activity, BookOpen, Music, Heart } from 'lucide-react';
import { MoodType, ActivityContent } from '../types';
import { moodColors, moodActivities } from '../utils/moodContent';

interface MoodContentProps {
  mood: MoodType;
  intensity: number;
  onBack: () => void;
  onActivitySelect: (activity: ActivityContent) => void;
}

const activityIcons: Record<ActivityContent['type'], React.ReactNode> = {
  breathing: <Activity className="w-5 h-5" />,
  journal: <BookOpen className="w-5 h-5" />,
  audio: <Music className="w-5 h-5" />,
  game: <Heart className="w-5 h-5" />,
  affirmation: <Heart className="w-5 h-5" />,
  music: <Music className="w-5 h-5" />
};

const moodMessages: Record<MoodType, string> = {
  happy: "I love seeing you so happy! Let's celebrate this wonderful feeling.",
  neutral: "Thank you for checking in. Let's explore what might be helpful right now.",
  anxious: "I can feel your anxiety, and that's completely okay. Let's find some calm together.",
  sad: "I'm here with you in this difficult moment. You're not alone.",
  angry: "Your anger is valid. Let's find a healthy way to work through these feelings.",
  tired: "You sound exhausted. Let's focus on rest and gentle care.",
  mixed: "Complex feelings are normal. Let's take this one step at a time."
};

export default function MoodContent({ mood, intensity, onBack, onActivitySelect }: MoodContentProps) {
  const activities = moodActivities[mood];
  const message = moodMessages[mood];

  return (
    <div className={`min-h-screen bg-gradient-to-br ${moodColors[mood]} p-4`}>
      <div className="max-w-md mx-auto">
        <div className="flex items-center mb-6">
          <button
            onClick={onBack}
            className="p-2 rounded-full bg-white/80 hover:bg-white transition-colors"
          >
            <ArrowLeft className="w-5 h-5 text-gray-600" />
          </button>
          <h1 className="ml-4 text-xl font-semibold text-gray-800">Your Safe Space</h1>
        </div>

        <div className="bg-white/90 backdrop-blur-sm rounded-3xl p-6 mb-6 shadow-lg">
          <div className="text-center">
            <div className="w-16 h-16 bg-gradient-to-r from-emerald-400 to-teal-400 rounded-full flex items-center justify-center mx-auto mb-4">
              <Heart className="w-8 h-8 text-white" />
            </div>
            <p className="text-gray-700 leading-relaxed">{message}</p>
            <div className="mt-4 text-sm text-gray-500">
              Intensity: <span className="font-semibold text-emerald-600">{intensity}/10</span>
            </div>
          </div>
        </div>

        <div className="space-y-3">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">What would help you right now?</h2>
          {activities.map((activity, index) => (
            <button
              key={index}
              onClick={() => onActivitySelect(activity)}
              className="w-full bg-white/90 backdrop-blur-sm rounded-2xl p-4 text-left hover:bg-white hover:shadow-lg transition-all duration-200 transform hover:scale-105"
            >
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-r from-emerald-400 to-teal-400 rounded-full flex items-center justify-center">
                  <div className="text-white">
                    {activityIcons[activity.type]}
                  </div>
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-800 mb-1">{activity.title}</h3>
                  <p className="text-sm text-gray-600">{activity.description}</p>
                  {activity.duration && (
                    <p className="text-xs text-emerald-600 mt-1">
                      ~{Math.floor(activity.duration / 60)} minutes
                    </p>
                  )}
                </div>
              </div>
            </button>
          ))}
        </div>

        <div className="mt-8 text-center">
          <p className="text-sm text-gray-600">
            Remember: You're safe, you're cared for, and this moment will pass. 💚
          </p>
        </div>
      </div>
    </div>
  );
}