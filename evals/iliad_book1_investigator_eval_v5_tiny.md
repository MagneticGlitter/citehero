# Iliad Book 1 Investigator v5 — tiny run (Q6)

This is a small comparison report for the refreshed investigator flow. It captures one exact question/output pair and is intended for comparison against v2/v3/v4.

## Q6. What does Hera suspect Zeus has done?

### Investigator response
```md
Question: What does Hera suspect Zeus has done?
Response: or else refuse it, you have nothing to fear, that I may know 515 by how much I am the most dishonoured of all gods.' Deeply disturbed Zeus who gathers the clouds answered her: 'This is a disastrous matter when you set me in conflict with Hera, and she troubles me with recriminations. [p. 15]
confident_in_ground: true
Evidence:
- [p. 15 | p0015_full] or else refuse it, you have nothing to fear, that I may know 515 by how much I am the most dishonoured of all gods.' Deeply disturbed Zeus who gathers the clouds answered her: 'This is a disastrous matter when you set me in conflict with Hera, and she troubles me with recriminations. Since even as things are, forever among the immortals 520 she is at me and speaks of how I help the Trojans in battle. Even so, go back again now, go away, for fear she see us. I will look to these things that they be accomplished.
- [p. 16 | p0016_full] For early in the morning she sat beside you and took your knees, and I think you bowed your head in assent to do honour to Achilleus, and to destroy many beside the ships of the Achaians.' Then in return Zeus who gathers the clouds made answer: 560 'Dear lady, I never escape you, you are always full of suspicion. Yet thus you can accomplish nothing surely, but be more distant from my heart than ever, and it will be the worse for you. If what you say is true, then that is the way I wish it. 565 But go then, sit down in silence, and do as I tell you, for fear all the gods, as many as are on Olympos, can do nothing if I come close and lay my unconquerable hands upon you.' He spoke, and the goddcss the ox-eyed lady Hera was frightened and went and sat down in silence wrenching her heart to obedience, 57o and all the Uranian gods in the house of Zeus werc troubled. Hephaistos the renowned smith rose up to speak among them, to bring comfort to his beloved mother, Hera of the white arms: 'Thi...
- [p. 3 | p0003_full] even an interpreter of dreams, since a dream also comes from Zeus, who can tell why Phoibos Apollo is so angry, if for the sake of some vow, some hecatomb he blames us, 65 if given the fragrant smoke of lambs, of he goats, somehow he can be made willing to beat the bane aside from us.' He spoke thus and sat down again, and among them stood up Kalchas, Thestor's son, far the best of the bird interpreters, who knew all things that were, the things to come and the things past, 70 who guided into the land of Ilion the ships of the Achaians through that seercraft of his own that Phoibos Apollo gave him. He in kind intention toward all stood forth and addressed them: 'You have bidden me, Achilleus beloved of Zeus, to explain to you this anger of Apollo the lord who strikes from afar. Then 75 I will speak; yet make me a promise and swear before me readily by word and work of your hands to defend me, since I believe I shall make a man angry who holds great kingship over the men of Argos, and a...
```

### Short evaluation
- retrieval_relevance: yes
- citation_accuracy: yes
- confident_in_ground: true
- answer_quality: good

## Comparison
- Compared with v4, this tiny run is much better for answer shape: it returns a short answer plus page citations instead of a fallback-only evidence dump.
- Compared with the earlier v2/v3/v4 style, the investigator is now clearly using citation-grounded retrieval as the answer source.
- The remaining issue is that the answer is still somewhat truncated/overlapping with quoted evidence, so the final response formatting still needs cleanup.

## Notes
- This report is intentionally tiny: one question only.
- It is grounded in the exact captured run for Q6.
