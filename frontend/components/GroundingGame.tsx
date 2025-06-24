import React, { useState, useEffect } from 'react';
import { ArrowLeft, CheckCircle, RotateCcw } from 'lucide-react';
import { MoodType } from '../types';
import { moodColors } from '../utils/moodContent';

interface GroundingGameProps {
  mood: MoodType;
  onBack: () => void;
}

const groundingGames = {
  '5-4-3-2-1': {
    title: '5-4-3-2-1 Grounding',
    description: 'Notice your surroundings to anchor yourself in the present moment.',
    steps: [
      { instruction: 'Name 5 things you can see', count: 5, type: 'see' },
      { instruction: 'Name 4 things you can touch', count: 4, type: 'touch' },
      { instruction: 'Name 3 things you can hear', count: 3, type: 'hear' },
      { instruction: 'Name 2 things you can smell', count: 2, type: 'smell' },
      { instruction: 'Name 1 thing you can taste', count: 1, type: 'taste' }
    ]
  },
  'color-hunt': {
    title: 'Color Hunt',
    description: 'Find objects of specific colors around you to focus your mind.',
    steps: [
      { instruction: 'Find 5 red things', count: 5, type: 'red' },
      { instruction: 'Find 4 blue things', count: 4, type: 'blue' },
      { instruction: 'Find 3 green things', count: 3, type: 'green' },
      { instruction: 'Find 2 yellow things', count: 2, type: 'yellow' },
      { instruction: 'Find 1 purple thing', count: 1, type: 'purple' }
    ]
  },
  'safe-space': {
    title: 'Safe Space Visualization',
    description: 'Think of people and places that make you feel safe and secure.',
    steps: [
      { instruction: 'Name 3 people who make you feel safe', count: 3, type: 'people' },
      { instruction: 'Name 2 places where you feel peaceful', count: 2, type: 'places' },
      { instruction: 'Name 1 memory that makes you smile', count: 1, type: 'memory' }
    ]
  }
};

export default function GroundingGame({ mood, onBack }: GroundingGameProps) {
  const [selectedGame, setSelectedGame] = useState<string | null>(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [currentItems, setCurrentItems] = useState<string[]>([]);
  const [currentInput, setCurrentInput] = useState('');
  const [completedSteps, setCompletedSteps] = useState<boolean[]>([]);
  const [gameComplete, setGameComplete] = useState(false);

  const gameKeys = Object.keys(groundingGames) as Array<keyof typeof groundingGames>;
  
  // Auto-select appropriate game based on mood
  useEffect(() => {
    if (mood === 'anxious') {
      setSelectedGame('5-4-3-2-1');
    } else if (mood === 'mixed' || mood === 'sad') {
      setSelectedGame('safe-space');
    } else {
      setSelectedGame('color-hunt');
    }
  }, [mood]);

  const currentGame = selectedGame ? groundingGames[selectedGame as keyof typeof groundingGames] : null;
  const currentStepData = currentGame?.steps[currentStep];

  const handleAddItem = () => {
    if (!currentInput.trim() || !currentStepData) return;

    const newItems = [...currentItems, currentInput.trim()];
    setCurrentItems(newItems);
    setCurrentInput('');

    // Check if step is complete
    if (newItems.length >= currentStepData.count) {
      const newCompletedSteps = [...completedSteps];
      newCompletedSteps[currentStep] = true;
      setCompletedSteps(newCompletedSteps);

      // Move to next step or complete game
      setTimeout(() => {
        if (currentStep < currentGame!.steps.length - 1) {
          setCurrentStep(prev => prev + 1);
          setCurrentItems([]);
        } else {
          setGameComplete(true);
        }
      }, 1000);
    }
  };

  const resetGame = () => {
    setCurrentStep(0);
    setCurrentItems([]);
    setCurrentInput('');
    setCompletedSteps([]);
    setGameComplete(false);
  };

  const selectGame = (gameKey: string) => {
    setSelectedGame(gameKey);
    resetGame();
  };

  if (!selectedGame || !currentGame) {
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
            <h1 className="ml-4 text-xl font-semibold text-gray-800">Choose a Grounding Game</h1>
          </div>

          <div className="space-y-4">
            {gameKeys.map((gameKey) => (
              <button
                key={gameKey}
                onClick={() => selectGame(gameKey)}
                className="w-full bg-white/90 backdrop-blur-sm rounded-2xl p-4 text-left hover:bg-white hover:shadow-lg transition-all duration-200"
              >
                <h3 className="font-semibold text-gray-800 mb-2">
                  {groundingGames[gameKey].title}
                </h3>
                <p className="text-sm text-gray-600">
                  {groundingGames[gameKey].description}
                </p>
              </button>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (gameComplete) {
    return (
      <div className={`min-h-screen bg-gradient-to-br ${moodColors[mood]} p-4 flex items-center justify-center`}>
        <div className="max-w-md mx-auto text-center">
          <div className="bg-white/90 backdrop-blur-sm rounded-3xl p-8">
            <div className="w-16 h-16 bg-gradient-to-r from-emerald-400 to-teal-400 rounded-full flex items-center justify-center mx-auto mb-4">
              <CheckCircle className="w-8 h-8 text-white" />
            </div>
            <h2 className="text-2xl font-bold text-gray-800 mb-4">Well Done! 🌟</h2>
            <p className="text-gray-600 mb-6">
              You've completed the grounding exercise. Take a moment to notice how you feel now compared to when you started.
            </p>
            <div className="flex space-x-3">
              <button
                onClick={resetGame}
                className="flex-1 flex items-center justify-center space-x-2 bg-emerald-500 hover:bg-emerald-600 text-white py-3 px-4 rounded-xl font-medium transition-colors"
              >
                <RotateCcw className="w-4 h-4" />
                <span>Try Again</span>
              </button>
              <button
                onClick={onBack}
                className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-800 py-3 px-4 rounded-xl font-medium transition-colors"
              >
                Done
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`min-h-screen bg-gradient-to-br ${moodColors[mood]} p-4`}>
      <div className="max-w-md mx-auto">
        <div className="flex items-center justify-between mb-6">
          <button
            onClick={() => setSelectedGame(null)}
            className="p-2 rounded-full bg-white/80 hover:bg-white transition-colors"
          >
            <ArrowLeft className="w-5 h-5 text-gray-600" />
          </button>
          <h1 className="text-lg font-semibold text-gray-800">{currentGame.title}</h1>
          <button
            onClick={resetGame}
            className="p-2 rounded-full bg-white/80 hover:bg-white transition-colors"
          >
            <RotateCcw className="w-5 h-5 text-gray-600" />
          </button>
        </div>

        {/* Progress indicator */}
        <div className="bg-white/90 backdrop-blur-sm rounded-2xl p-4 mb-6">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-600">Progress</span>
            <span className="text-sm text-gray-500">{currentStep + 1} of {currentGame.steps.length}</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-gradient-to-r from-emerald-400 to-teal-400 h-2 rounded-full transition-all duration-300"
              style={{ width: `${((currentStep + (currentItems.length / (currentStepData?.count || 1))) / currentGame.steps.length) * 100}%` }}
            />
          </div>
        </div>

        {/* Current step */}
        <div className="bg-white/90 backdrop-blur-sm rounded-2xl p-6 mb-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">
            {currentStepData?.instruction}
          </h3>

          {/* Input field */}
          <div className="flex space-x-2 mb-4">
            <input
              type="text"
              value={currentInput}
              onChange={(e) => setCurrentInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleAddItem()}
              placeholder="Type your answer..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-400 focus:border-transparent"
            />
            <button
              onClick={handleAddItem}
              disabled={!currentInput.trim()}
              className="px-4 py-2 bg-emerald-500 hover:bg-emerald-600 disabled:bg-gray-300 text-white rounded-xl font-medium transition-colors"
            >
              Add
            </button>
          </div>

          {/* Progress for current step */}
          <div className="text-center mb-4">
            <span className="text-2xl font-bold text-emerald-600">
              {currentItems.length}/{currentStepData?.count}
            </span>
            <p className="text-sm text-gray-600">items found</p>
          </div>

          {/* Listed items */}
          {currentItems.length > 0 && (
            <div className="space-y-2">
              {currentItems.map((item, index) => (
                <div key={index} className="flex items-center space-x-2 p-2 bg-emerald-50 rounded-lg">
                  <CheckCircle className="w-4 h-4 text-emerald-600" />
                  <span className="text-gray-700">{item}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Encouragement */}
        <div className="text-center">
          <p className="text-sm text-gray-600">
            Take your time. There are no wrong answers. 💚
          </p>
        </div>
      </div>
    </div>
  );
}