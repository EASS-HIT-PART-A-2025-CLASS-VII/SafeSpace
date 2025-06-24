import React, { useState, useEffect } from 'react';
import { ArrowLeft, Heart, RefreshCw, Play, Pause, Loader } from 'lucide-react';
import { MoodType } from '../types';
import { moodColors } from '../utils/moodContent';

interface AffirmationData {
  affirmations: string[];
  personalized_message: string;
  breathing_instruction?: string;
}

interface AffirmationsPlayerProps {
  mood: MoodType;
  intensity: number;
  onBack: () => void;
}

export default function AffirmationsPlayer({ mood, intensity, onBack }: AffirmationsPlayerProps) {
  const [affirmationData, setAffirmationData] = useState<AffirmationData | null>(null);
  const [currentAffirmation, setCurrentAffirmation] = useState(0);
  const [isAutoPlay, setIsAutoPlay] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    generateAffirmations();
  }, [mood, intensity]);

  useEffect(() => {
    if (isAutoPlay && affirmationData) {
      const interval = setInterval(() => {
        setCurrentAffirmation(prev => 
          prev < affirmationData.affirmations.length - 1 ? prev + 1 : 0
        );
      }, 8000); // Change every 8 seconds
      return () => clearInterval(interval);
    }
  }, [isAutoPlay, affirmationData]);

  const generateAffirmations = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Get auth token from localStorage
      const token = localStorage.getItem('auth_token');
      
      const response = await fetch('/api/ai/affirmations', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          mood_type: mood,
          intensity: intensity
        })
      });

      if (!response.ok) {
        throw new Error('Failed to generate affirmations');
      }

      const data = await response.json();
      setAffirmationData(data);
      setCurrentAffirmation(0);
    } catch (err) {
      setError('Unable to generate affirmations. Please try again.');
      console.error('Affirmations generation error:', err);
      
      // Fallback affirmations
      setAffirmationData({
        affirmations: [
          "I am worthy of love and compassion",
          "This feeling is temporary and will pass",
          "I have the strength to get through this",
          "I am doing my best, and that's enough",
          "I deserve peace and happiness"
        ],
        personalized_message: "You're taking great care of yourself by being here.",
        breathing_instruction: mood === 'anxious' ? "Take a slow, deep breath in for 4 counts, hold for 4, then exhale for 6 counts" : undefined
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleNext = () => {
    if (affirmationData) {
      setCurrentAffirmation(prev => 
        prev < affirmationData.affirmations.length - 1 ? prev + 1 : 0
      );
    }
  };

  const handlePrevious = () => {
    if (affirmationData) {
      setCurrentAffirmation(prev => 
        prev > 0 ? prev - 1 : affirmationData.affirmations.length - 1
      );
    }
  };

  if (isLoading) {
    return (
      <div className={`min-h-screen bg-gradient-to-br ${moodColors[mood]} p-4 flex items-center justify-center`}>
        <div className="bg-white/90 backdrop-blur-sm rounded-3xl p-8 text-center">
          <Loader className="w-12 h-12 animate-spin text-emerald-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-800 mb-2">Creating Your Affirmations</h2>
          <p className="text-gray-600">AI is crafting personalized messages just for you...</p>
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
          <h1 className="text-xl font-semibold text-gray-800">AI Affirmations</h1>
          <button
            onClick={generateAffirmations}
            className="p-2 rounded-full bg-white/80 hover:bg-white transition-colors"
          >
            <RefreshCw className="w-5 h-5 text-gray-600" />
          </button>
        </div>

        {affirmationData && (
          <>
            {/* Personalized Message */}
            <div className="bg-white/90 backdrop-blur-sm rounded-2xl p-6 mb-6">
              <div className="text-center">
                <div className="w-16 h-16 bg-gradient-to-r from-pink-400 to-purple-400 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Heart className="w-8 h-8 text-white" />
                </div>
                <p className="text-gray-700 leading-relaxed">{affirmationData.personalized_message}</p>
              </div>
            </div>

            {/* Current Affirmation */}
            <div className="bg-white/90 backdrop-blur-sm rounded-2xl p-8 mb-6 text-center">
              <div className="mb-6">
                <div className="text-4xl mb-4">✨</div>
                <p className="text-xl font-medium text-gray-800 leading-relaxed mb-4">
                  "{affirmationData.affirmations[currentAffirmation]}"
                </p>
                <div className="text-sm text-gray-500">
                  {currentAffirmation + 1} of {affirmationData.affirmations.length}
                </div>
              </div>

              {/* Navigation */}
              <div className="flex items-center justify-center space-x-4 mb-6">
                <button
                  onClick={handlePrevious}
                  className="p-3 rounded-full bg-gray-100 hover:bg-gray-200 transition-colors"
                >
                  <ArrowLeft className="w-5 h-5 text-gray-600" />
                </button>

                <button
                  onClick={() => setIsAutoPlay(!isAutoPlay)}
                  className={`p-4 rounded-full transition-colors ${
                    isAutoPlay 
                      ? 'bg-emerald-500 hover:bg-emerald-600 text-white' 
                      : 'bg-gray-100 hover:bg-gray-200 text-gray-600'
                  }`}
                >
                  {isAutoPlay ? (
                    <Pause className="w-6 h-6" />
                  ) : (
                    <Play className="w-6 h-6" />
                  )}
                </button>

                <button
                  onClick={handleNext}
                  className="p-3 rounded-full bg-gray-100 hover:bg-gray-200 transition-colors"
                >
                  <ArrowLeft className="w-5 h-5 text-gray-600 rotate-180" />
                </button>
              </div>

              {isAutoPlay && (
                <p className="text-sm text-emerald-600">
                  Auto-playing • Changes every 8 seconds
                </p>
              )}
            </div>

            {/* Breathing Instruction */}
            {affirmationData.breathing_instruction && (
              <div className="bg-gradient-to-r from-blue-100 to-purple-100 border border-blue-200 rounded-2xl p-4 mb-6">
                <h3 className="font-semibold text-blue-800 mb-2">💨 Breathing Exercise</h3>
                <p className="text-blue-700 text-sm">{affirmationData.breathing_instruction}</p>
              </div>
            )}

            {/* All Affirmations List */}
            <div className="bg-white/90 backdrop-blur-sm rounded-2xl p-4">
              <h3 className="font-semibold text-gray-800 mb-3">Your Affirmations</h3>
              <div className="space-y-2">
                {affirmationData.affirmations.map((affirmation, index) => (
                  <button
                    key={index}
                    onClick={() => setCurrentAffirmation(index)}
                    className={`w-full text-left p-3 rounded-xl transition-colors ${
                      index === currentAffirmation
                        ? 'bg-emerald-100 border border-emerald-200'
                        : 'hover:bg-gray-50'
                    }`}
                  >
                    <div className="flex items-start space-x-3">
                      <div className={`w-6 h-6 rounded-full flex items-center justify-center text-sm flex-shrink-0 mt-1 ${
                        index === currentAffirmation
                          ? 'bg-emerald-500 text-white'
                          : 'bg-gray-200 text-gray-600'
                      }`}>
                        {index + 1}
                      </div>
                      <p className="text-gray-700 leading-relaxed">"{affirmation}"</p>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Usage Tips */}
            <div className="mt-6 text-center">
              <p className="text-sm text-gray-600">
                💡 Repeat these affirmations whenever you need support
              </p>
            </div>
          </>
        )}
      </div>
    </div>
  );
}