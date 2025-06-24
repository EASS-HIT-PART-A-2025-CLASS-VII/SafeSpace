import React, { useState } from 'react';
import { ArrowLeft, Plus, Heart, Camera, Mic, Calendar, Trash2 } from 'lucide-react';
import { JoyMoment } from '../types';
import { useLocalStorage } from '../hooks/useLocalStorage';

interface JoyJarProps {
  onBack: () => void;
}

export default function JoyJar({ onBack }: JoyJarProps) {
  const [joyMoments, setJoyMoments] = useLocalStorage<JoyMoment[]>('joy-moments', []);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newMoment, setNewMoment] = useState({ title: '', description: '' });

  const handleAddMoment = () => {
    if (!newMoment.title.trim()) return;

    const moment: JoyMoment = {
      id: Date.now().toString(),
      title: newMoment.title,
      description: newMoment.description,
      timestamp: new Date()
    };

    setJoyMoments(prev => [moment, ...prev]);
    setNewMoment({ title: '', description: '' });
    setShowAddForm(false);
  };

  const deleteMoment = (id: string) => {
    setJoyMoments(prev => prev.filter(moment => moment.id !== id));
  };

  const getRandomMoment = () => {
    if (joyMoments.length === 0) return null;
    return joyMoments[Math.floor(Math.random() * joyMoments.length)];
  };

  const [randomMoment, setRandomMoment] = useState<JoyMoment | null>(null);

  const showRandomMoment = () => {
    const moment = getRandomMoment();
    setRandomMoment(moment);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-yellow-50 to-orange-50 p-4">
      <div className="max-w-md mx-auto">
        <div className="flex items-center justify-between mb-6">
          <button
            onClick={onBack}
            className="p-2 rounded-full bg-white/80 hover:bg-white transition-colors"
          >
            <ArrowLeft className="w-5 h-5 text-gray-600" />
          </button>
          <h1 className="text-xl font-semibold text-gray-800">Joy Jar ✨</h1>
          <button
            onClick={() => setShowAddForm(true)}
            className="p-2 rounded-full bg-yellow-400 hover:bg-yellow-500 transition-colors"
          >
            <Plus className="w-5 h-5 text-white" />
          </button>
        </div>

        <div className="bg-white/90 backdrop-blur-sm rounded-2xl p-6 mb-6 text-center">
          <div className="w-16 h-16 bg-gradient-to-r from-yellow-400 to-orange-400 rounded-full flex items-center justify-center mx-auto mb-4">
            <Heart className="w-8 h-8 text-white" />
          </div>
          <h2 className="text-lg font-semibold text-gray-800 mb-2">Your Happy Moments</h2>
          <p className="text-gray-600 text-sm mb-4">
            Collect your joyful moments to revisit when you need a smile.
          </p>
          
          {joyMoments.length > 0 && (
            <button
              onClick={showRandomMoment}
              className="bg-gradient-to-r from-yellow-400 to-orange-400 hover:from-yellow-500 hover:to-orange-500 text-white px-6 py-2 rounded-full font-medium transition-all transform hover:scale-105"
            >
              Surprise Me! 🎲
            </button>
          )}
        </div>

        {randomMoment && (
          <div className="bg-gradient-to-r from-yellow-100 to-orange-100 border border-yellow-200 rounded-2xl p-4 mb-6 animate-fadeIn">
            <div className="flex justify-between items-start mb-2">
              <h3 className="font-semibold text-yellow-800">{randomMoment.title}</h3>
              <button
                onClick={() => setRandomMoment(null)}
                className="text-yellow-600 hover:text-yellow-800"
              >
                ×
              </button>
            </div>
            <p className="text-yellow-700 text-sm mb-2">{randomMoment.description}</p>
            <p className="text-yellow-600 text-xs">
              {randomMoment.timestamp.toLocaleDateString()}
            </p>
          </div>
        )}

        {showAddForm && (
          <div className="bg-white/90 backdrop-blur-sm rounded-2xl p-6 mb-6 animate-fadeIn">
            <h3 className="font-semibold text-gray-800 mb-4">Add a Happy Moment</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  What made you happy?
                </label>
                <input
                  type="text"
                  value={newMoment.title}
                  onChange={(e) => setNewMoment(prev => ({ ...prev, title: e.target.value }))}
                  placeholder="e.g., Had coffee with my best friend"
                  className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Tell me more about it
                </label>
                <textarea
                  value={newMoment.description}
                  onChange={(e) => setNewMoment(prev => ({ ...prev, description: e.target.value }))}
                  placeholder="Describe what made this moment special..."
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-300 rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
                />
              </div>

              <div className="flex space-x-2">
                <button
                  onClick={handleAddMoment}
                  disabled={!newMoment.title.trim()}
                  className="flex-1 bg-gradient-to-r from-yellow-400 to-orange-400 hover:from-yellow-500 hover:to-orange-500 disabled:from-gray-300 disabled:to-gray-300 text-white py-2 px-4 rounded-xl font-medium transition-all"
                >
                  Save Moment
                </button>
                <button
                  onClick={() => setShowAddForm(false)}
                  className="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded-xl font-medium transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}

        {joyMoments.length === 0 ? (
          <div className="bg-white/90 backdrop-blur-sm rounded-2xl p-8 text-center">
            <div className="text-6xl mb-4">🫙</div>
            <h3 className="font-semibold text-gray-800 mb-2">Your Joy Jar is Empty</h3>
            <p className="text-gray-600 text-sm mb-4">
              Start collecting your happy moments! Every smile, laugh, and moment of joy deserves to be remembered.
            </p>
            <button
              onClick={() => setShowAddForm(true)}
              className="bg-gradient-to-r from-yellow-400 to-orange-400 hover:from-yellow-500 hover:to-orange-500 text-white px-6 py-2 rounded-full font-medium transition-all transform hover:scale-105"
            >
              Add Your First Moment
            </button>
          </div>
        ) : (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold text-gray-800">
                {joyMoments.length} Happy Moment{joyMoments.length !== 1 ? 's' : ''}
              </h3>
            </div>
            
            {joyMoments.map((moment) => (
              <div key={moment.id} className="bg-white/90 backdrop-blur-sm rounded-2xl p-4">
                <div className="flex justify-between items-start mb-2">
                  <h4 className="font-semibold text-gray-800 flex-1">{moment.title}</h4>
                  <button
                    onClick={() => deleteMoment(moment.id)}
                    className="ml-2 text-gray-400 hover:text-red-500 transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
                
                {moment.description && (
                  <p className="text-gray-600 text-sm mb-2">{moment.description}</p>
                )}
                
                <div className="flex items-center text-xs text-gray-500">
                  <Calendar className="w-3 h-3 mr-1" />
                  {moment.timestamp.toLocaleDateString()} at{' '}
                  {moment.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}