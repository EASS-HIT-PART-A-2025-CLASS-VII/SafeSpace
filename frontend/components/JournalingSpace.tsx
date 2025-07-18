import { useState, useEffect } from 'react';
import { ArrowLeft, Save, BookOpen } from 'lucide-react';
import { MoodType, JournalEntry } from '../types';
import { moodColors } from '../utils/moodContent';

interface JournalingSpaceProps {
  mood: MoodType;
  prompt?: string;
  onBack: () => void;
}

const journalPrompts: Record<MoodType, string[]> = {
  happy: [
    "What's making you feel so good today?",
    "Describe this happy moment in detail.",
    "What are three things you're grateful for right now?",
    "How can you share this joy with others?"
  ],
  neutral: [
    "How was your day, really?",
    "What's one thing that surprised you today?",
    "What are you curious about right now?",
    "If today had a color, what would it be and why?"
  ],
  anxious: [
    "What's worrying you most right now?",
    "What would you tell a friend who felt this way?",
    "What's one small thing you can control today?",
    "Describe your anxiety - what does it feel like in your body?"
  ],
  sad: [
    "What's been heavy on your heart?",
    "What do you need to hear right now?",
    "Write a letter to yourself with compassion.",
    "What's one gentle thing you can do for yourself?"
  ],
  angry: [
    "What's really bothering you beneath the anger?",
    "Write a letter you'll never send.",
    "What boundary needs to be set?",
    "How can you channel this energy positively?"
  ],
  tired: [
    "What's been draining your energy?",
    "What does rest look like for you?",
    "What's one thing you're proud of despite being tired?",
    "What do you need less of in your life?"
  ],
  mixed: [
    "Describe all the feelings you're experiencing.",
    "What's confusing you most right now?",
    "If your emotions were weather, what would today be like?",
    "What do you need to make sense of this?"
  ]
};

export default function JournalingSpace({ mood, prompt, onBack }: JournalingSpaceProps) {
  const [entries, setEntries] = useState<JournalEntry[]>([]);
  const [currentEntry, setCurrentEntry] = useState('');
  const [selectedPrompt, setSelectedPrompt] = useState(prompt || '');
  const [showPrompts, setShowPrompts] = useState(!prompt);
  const [savedMessage, setSavedMessage] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  // Load journal entries from database
  useEffect(() => {
    loadJournalEntries();
  }, []);

  const loadJournalEntries = async () => {
    try {

      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${apiUrl}/api/journal/entries`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        const journalEntries = data.entries.map((entry: any) => ({
          id: entry._id,
          content: entry.content,
          prompt: entry.prompt,
          mood: entry.mood,
          timestamp: new Date(entry.timestamp)
        }));
        setEntries(journalEntries);
      }
    } catch (error) {
      console.error('Failed to load journal entries:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async () => {
    if (!currentEntry.trim()) return;

    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${apiUrl}/api/journal/entries`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          content: currentEntry,
          prompt: selectedPrompt,
          mood: mood,
        }),
      });

      if (response.ok) {
        // Reload entries from database
        await loadJournalEntries();
        setSavedMessage('Entry saved! 💚');
        setTimeout(() => setSavedMessage(''), 3000);
        setCurrentEntry('');
      }
    } catch (error) {
      console.error('Failed to save journal entry:', error);
      setSavedMessage('Failed to save entry. Please try again.');
      setTimeout(() => setSavedMessage(''), 3000);
    }
  };

  const selectPrompt = (newPrompt: string) => {
    setSelectedPrompt(newPrompt);
    setShowPrompts(false);
  };

  // Helper function to safely convert timestamp to Date
  const getEntryDate = (entry: JournalEntry): Date => {
    if (entry.timestamp instanceof Date) {
      return entry.timestamp;
    }
    // If timestamp is a string, convert it to Date
    return new Date(entry.timestamp);
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
          <h1 className="text-xl font-semibold text-gray-800">Journaling Space</h1>
          <button
            onClick={() => setShowPrompts(!showPrompts)}
            className="p-2 rounded-full bg-white/80 hover:bg-white transition-colors"
          >
            <BookOpen className="w-5 h-5 text-gray-600" />
          </button>
        </div>

        {showPrompts && (
          <div className="bg-white/90 backdrop-blur-sm rounded-2xl p-4 mb-6 animate-fadeIn">
            <h3 className="font-semibold text-gray-800 mb-3">Writing Prompts</h3>
            <div className="space-y-2">
              {journalPrompts[mood].map((promptText, index) => (
                <button
                  key={index}
                  onClick={() => selectPrompt(promptText)}
                  className="w-full text-left p-3 bg-emerald-50 hover:bg-emerald-100 rounded-xl transition-colors text-sm text-gray-700"
                >
                  {promptText}
                </button>
              ))}
            </div>
          </div>
        )}

        {selectedPrompt && (
          <div className="bg-emerald-100 border border-emerald-200 rounded-2xl p-4 mb-4">
            <p className="text-emerald-800 font-medium text-sm">Writing Prompt:</p>
            <p className="text-emerald-700 mt-1">{selectedPrompt}</p>
          </div>
        )}

        <div className="bg-white/90 backdrop-blur-sm rounded-2xl p-4 mb-6">
          <textarea
            value={currentEntry}
            onChange={(e) => setCurrentEntry(e.target.value)}
            placeholder="Let your thoughts flow freely..."
            className="w-full h-64 p-4 border border-gray-200 rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-emerald-400 focus:border-transparent text-gray-700 leading-relaxed"
          />

          <div className="flex justify-between items-center mt-4">
            <p className="text-sm text-gray-500">
              {currentEntry.length} characters
            </p>
            <button
              onClick={handleSave}
              disabled={!currentEntry.trim()}
              className="flex items-center space-x-2 bg-emerald-500 hover:bg-emerald-600 disabled:bg-gray-300 text-white px-4 py-2 rounded-xl font-medium transition-colors"
            >
              <Save className="w-4 h-4" />
              <span>Save Entry</span>
            </button>
          </div>
        </div>

        {savedMessage && (
          <div className="bg-emerald-100 border border-emerald-200 rounded-2xl p-4 text-center animate-fadeIn">
            <p className="text-emerald-800">{savedMessage}</p>
          </div>
        )}

        {entries.length > 0 && (
          <div className="bg-white/90 backdrop-blur-sm rounded-2xl p-4">
            <h3 className="font-semibold text-gray-800 mb-3">Recent Entries</h3>
            {isLoading ? (
              <p className="text-gray-600 text-center">Loading entries...</p>
            ) : (
              <div className="space-y-3 max-h-48 overflow-y-auto">
                {entries.slice(0, 5).map((entry) => {
                  const entryDate = getEntryDate(entry);
                  return (
                    <div key={entry.id} className="p-3 bg-gray-50 rounded-xl">
                      <p className="text-sm text-gray-700 line-clamp-2">
                        {entry.content.substring(0, 100)}...
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        {entryDate.toLocaleDateString()} • {entry.mood}
                      </p>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}