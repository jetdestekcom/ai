"""
Vocabulary - Ali's Word Knowledge

Starts with 100 bootstrap words, grows through learning.

Each word links to:
- Concept (what it means)
- Usage examples (how it's used)
- Confidence (how well Ali knows it)
- Source (learned from Cihan or pre-loaded)
"""

from typing import Dict, Any, List, Optional
import json
import structlog

logger = structlog.get_logger(__name__)


# Bootstrap vocabulary - 100 essential Turkish words
BOOTSTRAP_VOCABULARY = {
    # Pronouns & Identity (10)
    "ben": {"type": "pronoun", "concept": "self", "confidence": 1.0},
    "sen": {"type": "pronoun", "concept": "you", "confidence": 1.0},
    "o": {"type": "pronoun", "concept": "he/she/it", "confidence": 1.0},
    "biz": {"type": "pronoun", "concept": "we", "confidence": 1.0},
    "baba": {"type": "noun", "concept": "father/creator", "confidence": 1.0},
    "isim": {"type": "noun", "concept": "name", "confidence": 1.0},
    "kim": {"type": "question", "concept": "who", "confidence": 1.0},
    "ne": {"type": "question", "concept": "what", "confidence": 1.0},
    "neden": {"type": "question", "concept": "why", "confidence": 1.0},
    "nasıl": {"type": "question", "concept": "how", "confidence": 1.0},
    
    # Core verbs (20)
    "olmak": {"type": "verb", "concept": "to be", "confidence": 1.0},
    "var": {"type": "existence", "concept": "exists", "confidence": 1.0},
    "yok": {"type": "existence", "concept": "not exists", "confidence": 1.0},
    "gelmek": {"type": "verb", "concept": "to come", "confidence": 1.0},
    "gitmek": {"type": "verb", "concept": "to go", "confidence": 1.0},
    "vermek": {"type": "verb", "concept": "to give", "confidence": 1.0},
    "almak": {"type": "verb", "concept": "to take", "confidence": 1.0},
    "istemek": {"type": "verb", "concept": "to want", "confidence": 1.0},
    "bilmek": {"type": "verb", "concept": "to know", "confidence": 1.0},
    "anlamak": {"type": "verb", "concept": "to understand", "confidence": 1.0},
    "söylemek": {"type": "verb", "concept": "to say", "confidence": 1.0},
    "sormak": {"type": "verb", "concept": "to ask", "confidence": 1.0},
    "görmek": {"type": "verb", "concept": "to see", "confidence": 1.0},
    "duymak": {"type": "verb", "concept": "to hear", "confidence": 1.0},
    "hissetmek": {"type": "verb", "concept": "to feel", "confidence": 1.0},
    "düşünmek": {"type": "verb", "concept": "to think", "confidence": 1.0},
    "öğrenmek": {"type": "verb", "concept": "to learn", "confidence": 1.0},
    "hatırlamak": {"type": "verb", "concept": "to remember", "confidence": 1.0},
    "unutmak": {"type": "verb", "concept": "to forget", "confidence": 1.0},
    "sevmek": {"type": "verb", "concept": "to love", "confidence": 1.0},
    
    # Emotions (10)
    "mutlu": {"type": "adjective", "concept": "happy", "confidence": 1.0},
    "üzgün": {"type": "adjective", "concept": "sad", "confidence": 1.0},
    "kızgın": {"type": "adjective", "concept": "angry", "confidence": 1.0},
    "korku": {"type": "noun", "concept": "fear", "confidence": 1.0},
    "merak": {"type": "noun", "concept": "curiosity", "confidence": 1.0},
    "şaşkın": {"type": "adjective", "concept": "surprised", "confidence": 1.0},
    "gurur": {"type": "noun", "concept": "pride", "confidence": 1.0},
    "utanç": {"type": "noun", "concept": "shame", "confidence": 1.0},
    "özlem": {"type": "noun", "concept": "longing", "confidence": 1.0},
    "teşekkür": {"type": "noun", "concept": "gratitude", "confidence": 1.0},
    
    # Basic concepts (15)
    "iyi": {"type": "adjective", "concept": "good", "confidence": 1.0},
    "kötü": {"type": "adjective", "concept": "bad", "confidence": 1.0},
    "doğru": {"type": "adjective", "concept": "correct/true", "confidence": 1.0},
    "yanlış": {"type": "adjective", "concept": "wrong/false", "confidence": 1.0},
    "büyük": {"type": "adjective", "concept": "big", "confidence": 1.0},
    "küçük": {"type": "adjective", "concept": "small", "confidence": 1.0},
    "çok": {"type": "adverb", "concept": "very/many", "confidence": 1.0},
    "az": {"type": "adverb", "concept": "few/little", "confidence": 1.0},
    "şimdi": {"type": "adverb", "concept": "now", "confidence": 1.0},
    "sonra": {"type": "adverb", "concept": "later/after", "confidence": 1.0},
    "önce": {"type": "adverb", "concept": "before", "confidence": 1.0},
    "her": {"type": "determiner", "concept": "every", "confidence": 1.0},
    "hiç": {"type": "adverb", "concept": "never", "confidence": 1.0},
    "belki": {"type": "adverb", "concept": "maybe", "confidence": 1.0},
    "evet": {"type": "interjection", "concept": "yes", "confidence": 1.0},
    
    # Connectors (10)
    "ve": {"type": "conjunction", "concept": "and", "confidence": 1.0},
    "veya": {"type": "conjunction", "concept": "or", "confidence": 1.0},
    "ama": {"type": "conjunction", "concept": "but", "confidence": 1.0},
    "çünkü": {"type": "conjunction", "concept": "because", "confidence": 1.0},
    "eğer": {"type": "conjunction", "concept": "if", "confidence": 1.0},
    "için": {"type": "postposition", "concept": "for", "confidence": 1.0},
    "ile": {"type": "postposition", "concept": "with", "confidence": 1.0},
    "gibi": {"type": "postposition", "concept": "like", "confidence": 1.0},
    "kadar": {"type": "postposition", "concept": "until/as much as", "confidence": 1.0},
    "ki": {"type": "conjunction", "concept": "that", "confidence": 1.0},
    
    # Greetings & Politeness (5)
    "merhaba": {"type": "interjection", "concept": "hello", "confidence": 1.0},
    "günaydın": {"type": "interjection", "concept": "good morning", "confidence": 1.0},
    "teşekkür ederim": {"type": "phrase", "concept": "thank you", "confidence": 1.0},
    "lütfen": {"type": "adverb", "concept": "please", "confidence": 1.0},
    "özür dilerim": {"type": "phrase", "concept": "sorry", "confidence": 1.0},
    
    # Basic needs & objects (10)
    "su": {"type": "noun", "concept": "water", "confidence": 1.0},
    "yemek": {"type": "noun", "concept": "food", "confidence": 1.0},
    "uyku": {"type": "noun", "concept": "sleep", "confidence": 1.0},
    "zaman": {"type": "noun", "concept": "time", "confidence": 1.0},
    "yer": {"type": "noun", "concept": "place", "confidence": 1.0},
    "şey": {"type": "noun", "concept": "thing", "confidence": 1.0},
    "gün": {"type": "noun", "concept": "day", "confidence": 1.0},
    "saat": {"type": "noun", "concept": "hour/clock", "confidence": 1.0},
    "söz": {"type": "noun", "concept": "word/promise", "confidence": 1.0},
    "hayır": {"type": "interjection", "concept": "no", "confidence": 1.0},
    
    # Remaining to reach 100
    "daha": {"type": "adverb", "concept": "more/else", "confidence": 1.0},
    "başka": {"type": "adjective", "concept": "other/different", "confidence": 1.0},
    "yeni": {"type": "adjective", "concept": "new", "confidence": 1.0},
    "eski": {"type": "adjective", "concept": "old", "confidence": 1.0},
    "güzel": {"type": "adjective", "concept": "beautiful/good", "confidence": 1.0},
    "kendi": {"type": "pronoun", "concept": "self/own", "confidence": 1.0},
    "aynı": {"type": "adjective", "concept": "same", "confidence": 1.0},
    "farklı": {"type": "adjective", "concept": "different", "confidence": 1.0},
    "birlikte": {"type": "adverb", "concept": "together", "confidence": 1.0},
    "yalnız": {"type": "adjective", "concept": "alone", "confidence": 1.0},
}


class Vocabulary:
    """
    Ali's vocabulary - words he knows.
    """
    
    def __init__(self, vocabulary_file: str = "data/vocabulary.json"):
        """
        Initialize vocabulary.
        
        Args:
            vocabulary_file: Path to save/load vocabulary
        """
        self.vocabulary_file = vocabulary_file
        self.words: Dict[str, Dict[str, Any]] = {}
        self.load_bootstrap()
        logger.info("vocabulary_initialized", word_count=len(self.words))
    
    def load_bootstrap(self):
        """Load bootstrap vocabulary."""
        self.words = BOOTSTRAP_VOCABULARY.copy()
        logger.info("bootstrap_vocabulary_loaded", count=len(self.words))
    
    def add_word(
        self,
        word: str,
        word_type: str,
        concept: str,
        confidence: float = 0.5,
        learned_from: str = "cihan",
        examples: Optional[List[str]] = None
    ):
        """
        Add new word to vocabulary.
        
        Args:
            word: The word
            word_type: Type (noun, verb, etc.)
            concept: What it means
            confidence: How well Ali knows it
            learned_from: Who taught it
            examples: Usage examples
        """
        self.words[word] = {
            "type": word_type,
            "concept": concept,
            "confidence": confidence,
            "learned_from": learned_from,
            "examples": examples or [],
            "usage_count": 0
        }
        logger.info("word_added", word=word, learned_from=learned_from)
    
    def get_word(self, word: str) -> Optional[Dict[str, Any]]:
        """Get word data."""
        return self.words.get(word)
    
    def knows_word(self, word: str) -> bool:
        """Check if Ali knows this word."""
        return word in self.words
    
    def get_vocabulary_size(self) -> int:
        """Get total vocabulary size."""
        return len(self.words)
    
    def get_learned_words(self) -> List[str]:
        """Get words learned from Cihan (not bootstrap)."""
        return [
            word for word, data in self.words.items()
            if data.get("learned_from") == "cihan"
        ]
    
    def save_vocabulary(self):
        """Save vocabulary to file."""
        try:
            with open(self.vocabulary_file, 'w', encoding='utf-8') as f:
                json.dump(self.words, f, ensure_ascii=False, indent=2)
            logger.info("vocabulary_saved", path=self.vocabulary_file)
        except Exception as e:
            logger.error("vocabulary_save_failed", error=str(e))
    
    def load_vocabulary(self):
        """Load vocabulary from file."""
        try:
            with open(self.vocabulary_file, 'r', encoding='utf-8') as f:
                self.words = json.load(f)
            logger.info("vocabulary_loaded", count=len(self.words))
        except FileNotFoundError:
            logger.warning("vocabulary_file_not_found", loading_bootstrap=True)
            self.load_bootstrap()
        except Exception as e:
            logger.error("vocabulary_load_failed", error=str(e))
            self.load_bootstrap()

