# Iliad Book 1 Investigator v5 — exact outputs (Q1–Q6)

This report compares the corrected investigator flow against v2/v3/v4 using exact captured outputs.

## Summary
- v2/v3/v4 often drifted toward evidence-dump / fallback style.
- v5 now produces short analytic answers with page citations and a `confident_in_ground` flag.
- For Q1–Q6, retrieval is solid and the response is now actually answering the question.

## Q1. Who is Chryses, and what does he ask the Achaians to do?

```md
Question: Who is Chryses, and what does he ask the Achaians to do?
Response: Chryses is Apollo’s priest. He asks the Achaians to return his daughter and accept his ransom [p. 1, 2, 13].
confident_in_ground: true
Evidence:
- [p. 1 | p0001_adjacent] What god was it then set them together in bitter collision? Zeus' son and Leto's, Apollo, who in anger at the king drove the foul pestilence along the host, and the people perished, I0 since Atreus' son had dishonoured Chryses, priest of Apollo, when he came beside the fast ships of the Achaians to ransom back his daughter, carrying gifts beyond count and holding in his hands wound on a staff of gold the ribbons of Apollo who strikes from afar, and supplicated all the Achaians, 15 but above all Atreus' two sons, the marshals of the people: 'Sons of Atreus and you other strong-greaved Achaians, to you may the gods grant who have their homes on Olympos Priam's city to be plundered and a fair homecoming thereafter, but may you give me back my own daughter and take the ransom, 20 giving honour to Zeus' son who strikes from afar, Apollo. Then all the rest of the Achaians cried out in favour that the priest be respected and the shining ransom be taken; yet this pleased not the heart of Atreu...
- [p. 13 | p0013_adjacent] Next they washed their hands and took up the scattering barley. Standing among them with lifted arms Chryses prayed in a great voice: 450 'Hear me, lord of the silver bow, who set your power about Chryse and Killa the sacrosanct, who are lord in strength over Tenedos; if once before you listened to my prayers and did me honour and smote strongly the host of the Achaians, so one more time bring to pass the wish that I pray for. 455 Beat aside at last the shameful plague from the Danaans.' So he spoke in prayer, and Phoibos Apollo heard him.
- [p. 2 | p0002_full] so First he went after the mules and the circling hounds, then let go a tearing arrow against the men themselves and struck them. The corpse fires burned everywhere and did not stop burning. Nine days up and down the host ranged the god's arrows, but on the tenth Achilleus called the people to assembly; 55 a thing put into his mind by the goddess of the white arms, Hera, who had pity upon the Danaans when she saw them dying. Now when they were all assembled in one place together, Achilleus of the swift feet stood up among them and spoke forth: 'Son of Atreus, I believe now that straggling backwards 60 we must make our way home if we can even escape death, if fighting now must crush the Achaians and the plague likewise. No, come, let us ask some holy man, some prophet, [60 ]
```

### Comparison
- v4/v3/v2 often returned raw evidence blocks; v5 gives an actual answer.
- The citation is page-based and the answer is direct.

## Q2. Who is Kalchas, and why is he afraid to speak?

```md
Question: Who is Kalchas, and why is he afraid to speak?
Response: Kalchas is a seer and bird-interpreter. He fears Agamemnon’s reaction because he must reveal that Apollo’s plague is punishment for Agamemnon’s dishonour of Chryses [p. 3, 9, 10, 15].
confident_in_ground: true
Evidence:
- [p. 3 | p0003_full] even an interpreter of dreams, since a dream also comes from Zeus, who can tell why Phoibos Apollo is so angry, if for the sake of some vow, some hecatomb he blames us, 65 if given the fragrant smoke of lambs, of he goats, somehow he can be made willing to beat the bane aside from us.' He spoke thus and sat down again, and among them stood up Kalchas, Thestor's son, far the best of the bird interpreters, who knew all things that were, the things to come and the things past, 70 who guided into the land of Ilion the ships of the Achaians through that seercraft of his own that Phoibos Apollo gave him. He in kind intention toward all stood forth and addressed them: 'You have bidden me, Achilleus beloved of Zeus, to explain to you this anger of Apollo the lord who strikes from afar. Then 75 I will speak; yet make me a promise and swear before me readily by word and work of your hands to defend me, since I believe I shall make a man angry who holds great kingship over the men of Argos, and a...
- [p. 9 | p0009_full] And if the everlasting gods have made him a spearman, 290 yet they have not given him the right to speak abusively.' Then looking at him darkly brilliant Achilleus answered him: 'So must I be called of no account and a coward if I must carry out every order you may happen to give me. Tell other men to do these things, but give me no more 295 commands, since I for my part have no intention to obey you. And put away in your thoughts this other thing I tell you. With my hands I will not fight for the girl's sake, neither with you nor any other man, since you take her away who gave her.
- [p. 15 | p0015_full] 530 So these two who had made their plans separated, and Thetis leapt down again from shining Olympos into the sea's depth, but Zeus went back to his own house, and all the gods rose up from their chairs to greet the coming of their father, not one had courage to keep his place as the father advanced, but stood up to greet him. 535 Thus he took his place on the throne; yet Hera was not ignorant, having seen how he had been plotting counsels with Thetis the silver-footed, the daughter of the sea's ancient, and at once she spoke revilingly to Zeus son of Kronos: 'Treacherous one, what god has been plotting counsels with you? 540 Always it is dear to your heart in my absence to think of secret things and decide upon them. Never have you patience frankly to speak forth to me the thing that you purpose.' Then to her the father of gods and men made answer: 'Hera, do not go on hoping that you will hear all my 545 thoughts, since these will be too hard for you, though you are my wife. Any thou...
- [p. 16 | p0016_full] Truly too much in time past I have not questioned nor probed you, but you are entirely free to think out whatever pleases you. Now, though, I am terribly afraid you were won over SSS by Thetis the silver-footed, the daughter of the sea's ancient. For early in the morning she sat beside you and took your knees, and I think you bowed your head in assent to do honour to Achilleus, and to destroy many beside the ships of the Achaians.' Then in return Zeus who gathers the clouds made answer: 560 'Dear lady, I never escape you, you are always full of suspicion. Yet thus you can accomplish nothing surely, but be more distant from my heart than ever, and it will be the worse for you. If what you say is true, then that is the way I wish it.
- [p. 10 | iliad_book1_p0010_c01] And Achilleus took no joy at all when he saw them. These two terrified and in awe of the king stood waiting quietly, and did not speak a word at all nor question him. But he knew the whole matter in his own heart, and spoke first: 'Welcome, heralds, messengers of Zeus and of mortals.
```

### Comparison
- v4/v3/v2 tended to stall at evidence; v5 explains the seer and the reason for fear.
- `confident_in_ground: true` is now explicit.

## Q3. Why does Apollo send a plague against the Achaians?

```md
Question: Why does Apollo send a plague against the Achaians?
Response: Apollo sends the plague because Agamemnon dishonours Chryses, refuses the ransom, and keeps Chryseis [p. 2, 3, 11, 13].
confident_in_ground: true
Evidence:
- [p. 3 | p0003_full] For a king when he is angry with a man beneath him is too strong, 80 and suppose even for the day itself he swallow down his anger, he still keeps bitterness that remains until its fulfilment deep in his chest. Speak forth then, tell me if you will protect me.' Then in answer again spoke Achilleus of the swift feet: 'Speak, interpreting whatever you know, and fear nothing. 85 In the name of Apollo beloved of Zeus to whom you, Kalchas, make your prayers when you interpret the gods' will to the Danaans, no man so long as I am alive above earth and see daylight shall lay the weight of his hands on you beside the hollow ships, not one of all the Danaans, even if you mean Agamemnon, 90 who now claims to be far the greatest of all the Achaians.' At this the blameless seer took courage again and spoke forth: 'No, it is not for the sake of some vow or hecatomb he blames us, but for the sake of his priest whom Agamemnon dishonoured and would not give him back his daughter nor accept the ransom....
- [p. 2 | p0002_full] so First he went after the mules and the circling hounds, then let go a tearing arrow against the men themselves and struck them. The corpse fires burned everywhere and did not stop burning. Nine days up and down the host ranged the god's arrows, but on the tenth Achilleus called the people to assembly; 55 a thing put into his mind by the goddess of the white arms, Hera, who had pity upon the Danaans when she saw them dying. Now when they were all assembled in one place together, Achilleus of the swift feet stood up among them and spoke forth: 'Son of Atreus, I believe now that straggling backwards 60 we must make our way home if we can even escape death, if fighting now must crush the Achaians and the plague likewise. No, come, let us ask some holy man, some prophet, [60 ]
- [p. 11 | p0011_full] We went against Thebe, the sacred city of Eëtion, and the city we sacked, and carried everything back to this place, and the sons of the Achaians made a fair distribution and for Atreus' son they chose out Chryseis of the fair cheeks. Then Chryses, priest of him who strikes from afar, Apollo, 370 came beside the fast ships of the bronze-armoured Achaians to ransom back his daughter, carrying gifts beyond count and holding in his hands wound on a staff of gold the ribbons of Apollo who strikes from afar, and supplicated all the Achaians, but above all Atreus' two sons, the marshals of the people. 375 Then all the rest of the Achaians cried out in favour that the priest be respected and the shining ransom be taken; yet this pleased not the heart of Atreus' son Agamemnon, but harshly he sent him away with a strong order upon him. The old man went back again in anger, but Apollo listened to his prayer, since he was very dear to him, and let go the wicked arrow against the Argives.
- [p. 13 | p0013_full] And the men arranged the sacred hecatomb for the god in orderly fashion around the strong-founded altar. Next they washed their hands and took up the scattering barley. Standing among them with lifted arms Chryses prayed in a great voice: 450 'Hear me, lord of the silver bow, who set your power about Chryse and Killa the sacrosanct, who are lord in strength over Tenedos; if once before you listened to my prayers and did me honour and smote strongly the host of the Achaians, so one more time bring to pass the wish that I pray for. 455 Beat aside at last the shameful plague from the Danaans.' So he spoke in prayer, and Phoibos Apollo heard him. And when all had made prayer and flung down the scattering barley first they drew back the victims' heads and slaughtered them and skinned them, and cut away the meat from the thighs and wrapped them in fat, 460 making a double fold, and laid shreds of flesh upon them. The old man burned these on a cleft stick and poured the gleaming wine over, wh...
```

### Comparison
- v4/v3/v2 often left this as a citation dump; v5 gives the causal explanation directly.
- The answer is concise and analysis-driven.

## Q4. Who asks Thetis to appeal to Zeus, and what does he want Zeus to do?

```md
Question: Who asks Thetis to appeal to Zeus, and what does he want Zeus to do?
Response: Achilles asks Thetis to appeal to Zeus so Zeus will help the Trojans and make the Achaeans suffer until Achilles is honoured [p. 4, 14, 15].
confident_in_ground: true
Evidence:
- [p. 14 | p0014_full] Afterwards they scattered to their own ships and their shelters. But that other still sat in anger beside his swift ships, Peleus' son divinely born, Achilleus of the swift feet. Never now would he go to assemblies where men win glory, 490 never more into battle, but continued to waste his heart out sitting there, though he longed always for the clamour and fighting. But when the twelfth dawn after this day appeared, the gods who live forever came back to Olympos all in a body and Zeus led them; nor did Thetis forget the entreaties 495 of her son, but she emerged from the sea's waves early in the morning and went up to the tall sky and Olympos. She found Kronos' broad-browed son apart from the others sitting upon the highest peak of rugged Olympos. goo She came and sat beside him with her left hand embracing his knees, but took him underneath the chin with her right hand and spoke in supplication to lord Zeus son of Kronos: 'Father Zeus, if ever before in word or action I did you favou...
- [p. 15 | p0015_full] I will look to these things that they be accomplished. See then, I will bend my head that you may believe me. For this among the immortal gods is the mightiest witness 525 I can give, and nothing I do shall be vain nor revocable nor a thing unfulfilled when I bend my head in assent to it.' He spoke, the son of Kronos, and nodded his head with the dark brows, and the immortally anointed hair of the great god swept from his divine head, and all Olympos was shaken. 530 So these two who had made their plans separated, and Thetis leapt down again from shining Olympos into the sea's depth, but Zeus went back to his own house, and all the gods rose up from their chairs to greet the coming of their father, not one had courage to keep his place as the father advanced, but stood up to greet him. 535 Thus he took his place on the throne; yet Hera was not ignorant, having seen how he had been plotting counsels with Thetis the silver-footed, the daughter of the sea's ancient, and at once she spoke...
- [p. 4 | p0004_full] Find me then some prize that shall be my own, lest I only among the Argives go without, since that were unfitting; 120 you are all witnesses to this thing, that my prize goes elsewhere.' Then in answer again spoke brilliant swift-footed Achilleus: 'Son of Atreus, most lordly, greediest for gain of all men, how shall the great-hearted Achaians give you a prize now? There is no great store of things lying about I know of. I25 But what we took from the cities by storm has been distributed; it is unbecoming for the people to call back things once given. No, for the present give the girl back to the god; we Achaians thrice and four times over will repay you, if ever Zeus gives into our hands the strong-walled citadel of Troy to be plundered. I30 Then in answer again spoke powerful Agamemnon: 'Not that way, good fighter though you be, godlike Achilleus, strive to cheat, for you will not deceive, you will not persuade me. What do you want? To keep your own prize and have me sit here lacking...
```

### Comparison
- v4/v3/v2 often missed the clear “Achilles asks Thetis” answer; v5 makes it explicit.
- Citation confidence is now recorded.

## Q5. What does Thetis ask Zeus to do for Achilles?

```md
Question: What does Thetis ask Zeus to do for Achilles?
Response: Thetis asks Zeus to honour Achilles by giving the Trojans the upper hand over the Achaeans [p. 7, 14, 15].
confident_in_ground: true
Evidence:
- [p. 14 | p0014_full] Afterwards they scattered to their own ships and their shelters. But that other still sat in anger beside his swift ships, Peleus' son divinely born, Achilleus of the swift feet. Never now would he go to assemblies where men win glory, 490 never more into battle, but continued to waste his heart out sitting there, though he longed always for the clamour and fighting. But when the twelfth dawn after this day appeared, the gods who live forever came back to Olympos all in a body and Zeus led them; nor did Thetis forget the entreaties 495 of her son, but she emerged from the sea's waves early in the morning and went up to the tall sky and Olympos. She found Kronos' broad-browed son apart from the others sitting upon the highest peak of rugged Olympos. goo She came and sat beside him with her left hand embracing his knees, but took him underneath the chin with her right hand and spoke in supplication to lord Zeus son of Kronos: 'Father Zeus, if ever before in word or action I did you favou...
- [p. 15 | p0015_full] I will look to these things that they be accomplished. See then, I will bend my head that you may believe me. For this among the immortal gods is the mightiest witness 525 I can give, and nothing I do shall be vain nor revocable nor a thing unfulfilled when I bend my head in assent to it.' He spoke, the son of Kronos, and nodded his head with the dark brows, and the immortally anointed hair of the great god swept from his divine head, and all Olympos was shaken. 530 So these two who had made their plans separated, and Thetis leapt down again from shining Olympos into the sea's depth, but Zeus went back to his own house, and all the gods rose up from their chairs to greet the coming of their father, not one had courage to keep his place as the father advanced, but stood up to greet him. 535 Thus he took his place on the throne; yet Hera was not ignorant, having seen how he had been plotting counsels with Thetis the silver-footed, the daughter of the sea's ancient, and at once she spoke...
- [p. 7 | p0007_full] Then in answer again spoke Achilleus of the swift feet: 215 'Goddess, it is necessary that I obey the word of you two, angry though I am in my heart. So it will be better. If any man obeys the gods, they listen to him also.' He spoke, and laid his heavy hand on the silver sword hilt and thrust the great blade back into the scabbard nor disobeyed 220 the word of Athene. And she went back again to Olympos to the house of Zeus of the aegis with the other divinities. But Peleus' son once again in words of derision spoke to Atreides, and did not yet let go of his anger: 'You wine sack, with a dog's eyes, with a deer's heart. Never 225 once have you taken courage in your heart to arm with your people for battle, or go into ambuscade with the best of the Achaians. No, for in such things you see death.
```

### Comparison
- v4/v3/v2 gave evidence only; v5 states the request directly.
- This is closer to the desired subagent behavior.

## Q6. What does Hera suspect Zeus has done?

```md
Question: What does Hera suspect Zeus has done?
Response: Hera suspects Zeus has secretly met with Thetis and agreed to help Achilles by favoring the Trojans against the Achaeans [p. 3, 15, 16].
confident_in_ground: true
Evidence:
- [p. 15 | p0015_full] or else refuse it, you have nothing to fear, that I may know 515 by how much I am the most dishonoured of all gods.' Deeply disturbed Zeus who gathers the clouds answered her: 'This is a disastrous matter when you set me in conflict with Hera, and she troubles me with recriminations. Since even as things are, forever among the immortals 520 she is at me and speaks of how I help the Trojans in battle. Even so, go back again now, go away, for fear she see us. I will look to these things that they be accomplished.
- [p. 16 | p0016_full] For early in the morning she sat beside you and took your knees, and I think you bowed your head in assent to do honour to Achilleus, and to destroy many beside the ships of the Achaians.' Then in return Zeus who gathers the clouds made answer: 560 'Dear lady, I never escape you, you are always full of suspicion. Yet thus you can accomplish nothing surely, but be more distant from my heart than ever, and it will be the worse for you. If what you say is true, then that is the way I wish it. 565 But go then, sit down in silence, and do as I tell you, for fear all the gods, as many as are on Olympos, can do nothing if I come close and lay my unconquerable hands upon you.' He spoke, and the goddcss the ox-eyed lady Hera was frightened and went and sat down in silence wrenching her heart to obedience, 57o and all the Uranian gods in the house of Zeus werc troubled. Hephaistos the renowned smith rose up to speak among them, to bring comfort to his beloved mother, Hera of the white arms: 'Thi...
- [p. 3 | p0003_full] even an interpreter of dreams, since a dream also comes from Zeus, who can tell why Phoibos Apollo is so angry, if for the sake of some vow, some hecatomb he blames us, 65 if given the fragrant smoke of lambs, of he goats, somehow he can be made willing to beat the bane aside from us.' He spoke thus and sat down again, and among them stood up Kalchas, Thestor's son, far the best of the bird interpreters, who knew all things that were, the things to come and the things past, 70 who guided into the land of Ilion the ships of the Achaians through that seercraft of his own that Phoibos Apollo gave him. He in kind intention toward all stood forth and addressed them: 'You have bidden me, Achilleus beloved of Zeus, to explain to you this anger of Apollo the lord who strikes from afar. Then 75 I will speak; yet make me a promise and swear before me readily by word and work of your hands to defend me, since I believe I shall make a man angry who holds great kingship over the men of Argos, and a...
```

### Comparison
- v4/v3/v2 were mostly evidence-dumps here; v5 makes the inference explicit.
- This is the first version that clearly answers the question instead of quoting it.

## Overall comparison
v5 is materially better for this workflow because it now returns an actual cited answer plus `confident_in_ground`, instead of only surfacing evidence. It is the right shape for comparing against v2/v3/v4.

## Notes
- This is a tiny comparison run, not the full 18-question benchmark.
- The exact outputs above were captured from the current investigator flow.
