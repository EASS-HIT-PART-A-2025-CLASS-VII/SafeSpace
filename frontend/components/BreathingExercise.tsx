import React, { useState, useEffect } from 'react';
import { ArrowLeft, Play, Pause, RotateCcw } from 'lucide-react';
import { MoodType } from '../types';
import { moodColors } from '../utils/moodContent';

interface BreathingExerciseProps {
  mood: MoodType;
  duration: number;
  onBack: () => void;
}

const breathingPatterns: Record<string, { inhale: number; hold: number; exhale: number; hold2?: number }> = {
  '4-7-8': { inhale: 4, hold: 7, exhale: 8 },
  'box': { inhale: 4, hold: 4, exhale: 4, hold2: 4 },
  'gentle': { inhale: 4, hold: 2, exhale: 6 },
  'calming': { inhale: 6, hold: 2, exhale: 8 }
};

export default function BreathingExercise({ mood, duration, onBack }: BreathingExerciseProps) {
  const [isActive, setIsActive] = useState(false);
  const [currentPhase, setCurrentPhase] = useState<'inhale' | 'hold' | 'exhale' | 'hold2'>('inhale');
  const [phaseTime, setPhaseTime] = useState(0);
  const [totalTime, setTotalTime] = useState(0);
  const [breathCount, setBreathCount] = useState(0);

  // Select breathing pattern based on mood
  const patternName = mood === 'anxious' ? '4-7-8' : mood === 'angry' ? 'box' : 'gentle';
  const pattern = breathingPatterns[patternName];

  const phaseMessages = {
    inhale: 'Breathe in slowly...',
    hold: 'Hold your breath...',
    exhale: 'Breathe out gently...',
    hold2: 'Rest...'
  };

  useEffect(() => {
    if (!isActive) return;

    const interval = setInterval(() => {
      setPhaseTime(prev => prev + 1);
      setTotalTime(prev => prev + 1);

      // Check if current phase is complete
      const currentDuration = pattern[currentPhase] || 0;
      if (phaseTime >= currentDuration) {
        setPhaseTime(0);
        
        // Move to next phase
        if (currentPhase === 'inhale') {
          setCurrentPhase('hold');
        } else if (currentPhase === 'hold') {
          setCurrentPhase('exhale');
        } else if (currentPhase === 'exhale') {
          if (pattern.hold2) {
            setCurrentPhase('hold2');
          } else {
            setCurrentPhase('inhale');
            setBreathCount(prev => prev + 1);
          }
        } else if (currentPhase === 'hold2') {
          setCurrentPhase('inhale');
          setBreathCount(prev => prev + 1);
        }
      }

      // Auto-stop when duration is reached
      if (totalTime >= duration) {
        setIsActive(false);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [isActive, currentPhase, phaseTime, totalTime, duration, pattern]);

  const handleStart = () => {
    setIsActive(true);
  };

  const handlePause = () => {
    setIsActive(false);
  };

  const handleReset = () => {
    setIsActive(false);
    setCurrentPhase('inhale');
    setPhaseTime(0);
    setTotalTime(0);
    setBreathCount(0);
  };

  const getCircleScale = () => {
    const progress = phaseTime / (pattern[currentPhase] || 1);
    if (currentPhase === 'inhale') return 1 + progress * 0.5;
    if (currentPhase === 'exhale') return 1.5 - progress * 0.5;
    return currentPhase === 'hold' || currentPhase === 'hold2' ? 1.5 : 1;
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className={`min-h-screen bg-gradient-to-br ${moodColors[mood]} p-4`}>
      <div className="max-w-md mx-auto">
        <div className="flex items-center justify-between mb-8">
          <button
            onClick={onBack}
            className="p-2 rounded-full bg-white/80 hover:bg-white transition-colors"
          >
            <ArrowLeft className="w-5 h-5 text-gray-600" />
          </button>
          <h1 className="text-xl font-semibold text-gray-800">Breathing Exercise</h1>
          <div className="w-9"></div>
        </div>

        <div className="text-center mb-8">
          <div className="relative">
            {/* Breathing circle */}
            <div 
              className="w-48 h-48 mx-auto rounded-full bg-gradient-to-r from-emerald-400 to-teal-400 shadow-2xl transition-transform duration-1000 ease-in-out flex items-center justify-center"
              style={{ transform: `scale(${getCircleScale()})` }}
            >
              <div className="text-white text-center">
                <div className="text-2xl font-light mb-2">
                  {currentPhase === 'inhale' && '↑'}
                  {currentPhase === 'hold' && '○'}
                  {currentPhase === 'exhale' && '↓'}
                  {currentPhase === 'hold2' && '○'}
                </div>
                <div className="text-lg font-medium">
                  {pattern[currentPhase] - phaseTime}
                </div>
              </div>
            </div>
          </div>

          <div className="mt-8 mb-6">
            <p className="text-lg font-medium text-gray-800 mb-2">
              {phaseMessages[currentPhase]}
            </p>
            <p className="text-sm text-gray-600">
              Pattern: {patternName.toUpperCase()}
            </p>
          </div>

          <div className="flex justify-center space-x-4 mb-8">
            {!isActive ? (
              <button
                onClick={handleStart}
                className="flex items-center space-x-2 bg-emerald-500 hover:bg-emerald-600 text-white px-6 py-3 rounded-full font-medium transition-colors"
              >
                <Play className="w-5 h-5" />
                <span>Start</span>
              </button>
            ) : (
              <button
                onClick={handlePause}
                className="flex items-center space-x-2 bg-orange-500 hover:bg-orange-600 text-white px-6 py-3 rounded-full font-medium transition-colors"
              >
                <Pause className="w-5 h-5" />
                <span>Pause</span>
              </button>
            )}
            
            <button
              onClick={handleReset}
              className="flex items-center space-x-2 bg-gray-500 hover:bg-gray-600 text-white px-6 py-3 rounded-full font-medium transition-colors"
            >
              <RotateCcw className="w-5 h-5" />
              <span>Reset</span>
            </button>
          </div>

          <div className="bg-white/90 backdrop-blur-sm rounded-2xl p-4">
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <p className="text-2xl font-bold text-emerald-600">{breathCount}</p>
                <p className="text-sm text-gray-600">Breaths</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-emerald-600">{formatTime(totalTime)}</p>
                <p className="text-sm text-gray-600">Time</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-emerald-600">{formatTime(duration - totalTime)}</p>
                <p className="text-sm text-gray-600">Remaining</p>
              </div>
            </div>
          </div>
        </div>

        {totalTime >= duration && (
          <div className="bg-emerald-100 border border-emerald-200 rounded-2xl p-4 text-center animate-fadeIn">
            <p className="text-emerald-800 font-medium">
              🌟 Great job! You've completed your breathing exercise.
            </p>
            <p className="text-emerald-600 text-sm mt-1">
              Take a moment to notice how you feel now.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}