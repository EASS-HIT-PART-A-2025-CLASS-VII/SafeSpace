import { MoodType, ActivityContent } from '../types';

export const moodColors: Record<MoodType, string> = {
  happy: 'from-yellow-300/20 to-orange-300/20',
  neutral: 'from-gray-300/20 to-blue-300/20',
  anxious: 'from-purple-300/20 to-pink-300/20',
  sad: 'from-blue-400/20 to-indigo-400/20',
  angry: 'from-red-300/20 to-orange-400/20',
  tired: 'from-indigo-300/20 to-purple-400/20',
  mixed: 'from-green-300/20 to-teal-300/20'
};

export const moodEmojis: Record<MoodType, string> = {
  happy: '😊',
  neutral: '😐',
  anxious: '😰',
  sad: '😢',
  angry: '😠',
  tired: '😴',
  mixed: '🤔'
};

export const moodActivities: Record<MoodType, ActivityContent[]> = {
  happy: [
    { type: 'music', title: 'AI Celebration Playlist', description: 'Uplifting music curated by AI to match your joy' },
    { type: 'journal', title: 'Joy Jar Entry', description: 'Capture this feeling to revisit later' },
    { type: 'affirmation', title: 'Positive Affirmations', description: 'AI-generated affirmations to amplify your happiness' }
  ],
  neutral: [
    { type: 'journal', title: 'Daily Reflection', description: 'Tell me about your day' },
    { type: 'breathing', title: 'Gentle Breathing', description: 'Soft breathing to center yourself', duration: 300 },
    { type: 'music', title: 'Balanced Playlist', description: 'AI-curated music for contemplation' }
  ],
  anxious: [
    { type: 'breathing', title: '4-7-8 Breathing', description: 'Calm your nervous system', duration: 480 },
    { type: 'affirmation', title: 'Calming Affirmations', description: 'AI-powered reassurance and grounding' },
    { type: 'game', title: 'Grounding Game', description: '5-4-3-2-1 sensory grounding exercise' },
    { type: 'music', title: 'Anxiety Relief Playlist', description: 'AI-selected calming music for anxiety' }
  ],
  sad: [
    { type: 'affirmation', title: 'Compassionate Affirmations', description: 'AI-generated comfort for difficult moments' },
    { type: 'journal', title: 'Express Your Feelings', description: 'Sometimes writing helps' },
    { type: 'music', title: 'Healing Music', description: 'AI-curated gentle music for emotional support' },
    { type: 'breathing', title: 'Healing Breath', description: 'Breathe through the sadness', duration: 420 }
  ],
  angry: [
    { type: 'breathing', title: 'Cooling Breath', description: 'Box breathing to release tension', duration: 360 },
    { type: 'affirmation', title: 'Grounding Affirmations', description: 'AI-powered messages to channel your energy' },
    { type: 'journal', title: 'Release Writing', description: 'Write out your frustrations safely' },
    { type: 'music', title: 'Energy Release Playlist', description: 'AI-selected music to channel anger positively' }
  ],
  tired: [
    { type: 'affirmation', title: 'Rest Permission', description: 'AI-generated reminders that you deserve rest' },
    { type: 'breathing', title: 'Restorative Breathing', description: 'Gentle breath for tired souls', duration: 600 },
    { type: 'music', title: 'Peaceful Rest Playlist', description: 'AI-curated sounds for restoration' },
    { type: 'journal', title: 'Gentle Reflection', description: 'What\'s one thing you\'re proud of today?' }
  ],
  mixed: [
    { type: 'journal', title: 'Free Writing', description: 'Write whatever comes to mind' },
    { type: 'breathing', title: 'Centering Breath', description: 'Find your center in complexity', duration: 450 },
    { type: 'affirmation', title: 'Understanding Affirmations', description: 'AI support for complex emotions' },
    { type: 'music', title: 'Complex Emotions Playlist', description: 'AI-curated music for mixed feelings' }
  ]
};

export const crisisKeywords = [
  'suicide', 'kill myself', 'end it all', 'hurt myself', 'self harm',
  'want to die', 'better off dead', 'can\'t go on', 'hopeless'
];

export const crisisResponse = {
  message: "I'm really concerned about you right now. You're not alone, and there are people who want to help.",
  resources: [
    { name: "National Suicide Prevention Lifeline", number: "988", available: "24/7" },
    { name: "Crisis Text Line", number: "Text HOME to 741741", available: "24/7" },
    { name: "International Association for Suicide Prevention", url: "https://www.iasp.info/resources/Crisis_Centres/" }
  ]
};