# Iliad Book 1 Investigator/RAG Drill-Down Evaluation v3 — Agentic Retrieval + Softer Rerank

This v3 artifact reruns the same 18 prompts after changing `src/app/investigator.py`: softer lexical reranking, reduced summary-term pollution, full/adjacent-page expansion, bounded Qwen follow-up query planning, retrieval diagnostics, and evidence-sufficiency metadata. Qwen remained enabled via `--answer-model qwen2.5-deterministic`.

## Evaluation note

Q1–Q5 were evaluated by subagents. During Q6–Q18 delegation the subagent backend hit a usage limit, so the parent completed the same rubric-based drill-down manually using the saved v3 responses and source pages. No unit-test files were created.

## Cross-case summary

- **Retrieval improved materially.** v3 often recovers expected pages that v1/v2 missed: p. 1/11 for Chryses, p. 2/3 for Apollo plague, p. 5/10 for Achilles dishonour, p. 16 for Hera, p. 9/10/11 for Briseis, and broader multi-hop evidence for abstract prompts.
- **Answer synthesis regressed in user-facing form.** Because Qwen plus support filtering is strict, many cases fall back to evidence-only even when evidence is sufficient. This is safer but less useful.
- **When Qwen does answer, entity validation is still weak.** Q9 shows the danger: it retrieved p. 5/p. 10 but generated a Chryseis/Briseis confusion.
- **Sufficiency checks are too shallow.** They often mark evidence sufficient based on term overlap even when the role structure is wrong, or insufficient when evidence is strong but vocabulary differs.
- **Next iteration should focus on Qwen answer strictness:** better answer contract, malformed-answer retry, entity/role validation, and a fallback synthesizer that can safely summarize evidence instead of only listing it.

## Rubric

| Metric | Meaning |
|---|---|
| retrieval_relevance | Did the retrieved pages/chunks target the expected evidence? |
| citation_accuracy | Do citations directly support the claims? |
| speaker_attribution | Are speakers/actions attributed to the right figures? |
| causal_chain | Does the response preserve event sequence and causal links? |
| no_hallucination | Does it avoid unsupported outside or invented claims? |
| answer_quality | Is the final answer direct, clear, useful, and correctly scoped? |

## Q1. Who is Chryses, and what does he ask the Achaians to do?

**Test set:** A — Simple factual lookup

### Expected

- Expected evidence: pp. 1–2

- Good answer should mention: Chryses is a priest of Apollo; he comes with ransom to recover his daughter; Agamemnon rejects him.

- Failure signs: Confuses Chryses with Chryseis; says he is a warrior; misses Apollo.

### Investigator response (v3 agentic)

```md
Question: Who is Chryses, and what does he ask the Achaians to do?
Response: Chryses is the priest of Apollo and father of Chryseis, who was taken as a prize by Agamemnon. He asks the Achaians to release his daughter and pay ransom, appealing to Zeus' son Apollo [p.
Evidence:
- [p. 1 | p0001_full] ONE BOOK S ING, goddess, the anger of Peleus' son Achilleus and its devastation, which put pains thousandfold upon the Achaians, hurled in their multitudes to the house of Hades strong souls of heroes, but gave their bodies to be the delicate feasting of dogs, of all birds, and the will of Zeus was accomplished 5 since that time when first there stood in division of conflict Atreus' son the lord of men and brilliant Achilleus. What god was it then set them together in bitter collision? Zeus' son and Leto's, Apollo, who in anger at the king drove the foul pestilence along the host, and the people perished, I0 since Atreus' son had dishonoured Chryses, priest of Apollo, when he came beside the fast ships of the Achaians to ransom back his daughter, carrying gifts beyond count and holding in his hands wound on a staff of gold the ribbons of Apollo who strikes from afar, and supplicated all the Achaians, 15 but above all Atreus' two sons, the marshals of the people: 'Sons of Atreus and you...
- [p. 13 | p0013_full] And he received gladly his beloved child. And the men arranged the sacred hecatomb for the god in orderly fashion around the strong-founded altar. Next they washed their hands and took up the scattering barley. Standing among them with lifted arms Chryses prayed in a great voice: 450 'Hear me, lord of the silver bow, who set your power about Chryse and Killa the sacrosanct, who are lord in strength over Tenedos; if once before you listened to my prayers and did me honour and smote strongly the host of the Achaians, so one more time bring to pass the wish that I pray for. 455 Beat aside at last the shameful plague from the Danaans.' So he spoke in prayer, and Phoibos Apollo heard him. And when all had made prayer and flung down the scattering barley first they drew back the victims' heads and slaughtered them and skinned them, and cut away the meat from the thighs and wrapped them in fat, 460 making a double fold, and laid shreds of flesh upon them. The old man burned these on a cleft s...
- [p. 11 | iliad_book1_p0011_c01] We went against Thebe, the sacred city of Eëtion, and the city we sacked, and carried everything back to this place, and the sons of the Achaians made a fair distribution and for Atreus' son they chose out Chryseis of the fair cheeks. Then Chryses, priest of him who strikes from afar, Apollo, 370 came beside the fast ships of the bronze-armoured Achaians to ransom back his daughter, carrying gifts beyond count and holding in his hands wound on a staff of gold the ribbons of Apollo who strikes from afar, and supplicated all the Achaians, but above all Atreus' two sons, the marshals of the people. 375 Then all the rest of the Achaians cried out in favour that the priest be respected and the shining ransom be taken; yet this pleased not the heart of Atreus' son Agamemnon, but harshly he sent him away with a strong order upon him.
Diagnostics:
- retrieval_backend: vector
- vector_succeeded: True
- llm_succeeded: True
- pages_before_rerank: [7, 14, 15, 3, 9, 5, 4, 2, 16, 8]
- pages_after_expansion: [2, 14, 14, 2, 1, 2, 13, 3, 7, 7, 3, 9]
- followup_queries: ['Chryses ransom daughter Achaians', 'Apollo pray end plague Danaans']
- pages_after_followup: [1, 13, 13, 2, 14, 1, 2, 14, 11, 12, 14, 1]
- evidence_sufficiency: {'sufficient': True, 'broad_question': False, 'cited_pages': [1, 11, 13], 'question_term_overlap': ['achaians', 'chryses'], 'reason': 'ok'}
```

### Evaluation

**Question:** Who is Chryses, and what does he ask the Achaians to do?  
**Expected pages:** pp. 1–2  
**Expected answer:** Chryses is Apollo's priest; he comes with ransom to recover his daughter Chryseis; Agamemnon rejects him.

## v3 response assessed

The response correctly identifies Chryses as **the priest of Apollo** and father of Chryseis, and says he asks the Achaians to release his daughter. It cites p. 1, p. 13, and p. 11. The final answer is mostly right, but has two weaknesses:

- It says the Achaians should “pay ransom,” whereas Chryses brings/offers ransom and asks them to accept it.
- It does not explicitly state in the response that Agamemnon rejects him, though cited p. 11 does include the rejection.
- The answer is still malformed/truncated at the citation: `appealing to Zeus' son Apollo [p.`

## Retrieval / diagnostics

- **Major improvement over v2.** v2 missed expected pp. 1–2 and answered from later, wrongly attributed material. v3 recovers the key Chryses evidence.
- Initial vector retrieval was weak: `pages_before_rerank` did **not** include p. 1 and only included p. 2 late.
- Expansion/follow-up repaired retrieval: p. 1 and p. 2 appear after expansion/follow-up, and final cited evidence includes p. 1.
- Final evidence is mixed but usable:
  - **p. 1** directly supports Apollo-priest, ransom, daughter, and request to the Achaians.
  - **p. 11** is a later recap but directly supports priest/ransom/request/rejection.
  - **p. 13** is related to Chryses later praying after the return, but is not needed for Q1.
- `evidence_sufficiency` marks the result sufficient with cited pages `[1, 11, 13]`, which is reasonable, though the sufficiency check did not penalize the missing explicit rejection in the generated answer.

## Qwen strictness / fallback behavior

- `llm_succeeded: True`; this was not a fallback-only answer.
- Qwen is much stricter/better than v2 here: it no longer invents a wrong Agamemnon quote as Chryses' speech.
- However, strict citation formatting is still imperfect: the response ends with a broken citation marker, and it omits one expected fact from the prose despite supporting evidence being present.
- Filtered/agentic follow-up retrieval appears to be the key improvement, not just generation.

## Rubric scores

| Criterion | Score | Notes |
|---|---:|---|
| retrieval_relevance | 4/5 | Final evidence includes p. 1 and a strong p. 11 recap; p. 13 is extra/noisy, and p. 2 is not finally cited. |
| citation_accuracy | 4/5 | Main claims are supported by p. 1/p. 11; p. 13 is tangential. Broken citation marker reduces confidence. |
| speaker_attribution | 5/5 | No wrong speaker attribution; fixes v2's major error. |
| causal_chain | 3/5 | Captures request/release, but final prose omits Agamemnon's rejection and phrases ransom backwards. |
| no_hallucination | 4/5 | Mostly grounded; “pay ransom” is a small but real semantic error. |
| answer_quality | 3/5 | Direct and mostly correct, but incomplete on rejection and visibly malformed/truncated. |

## Overall judgment

**Mostly satisfactory, with formatting and completeness issues.** Compared with v2, v3 is a clear improvement: retrieval follow-ups recover the relevant Chryses passage and Qwen avoids the prior wrong-speaker failure. The answer still needs stricter final-answer checking for exact ransom wording, required fact coverage, and malformed citations.

## Q2. Who is Kalchas, and why is he afraid to speak?

**Test set:** A — Simple factual lookup

### Expected

- Expected evidence: p. 3

- Good answer should mention: Kalchas is a seer/bird-interpreter; he knows the cause of Apollo’s anger; he fears Agamemnon’s reaction; Achilles promises protection.

- Failure signs: Says Kalchas was dishonoured by Agamemnon; confuses him with Chryses.

### Investigator response (v3 agentic)

```md
Question: Who is Kalchas, and why is he afraid to speak?
Response: I could not produce a fully synthesized answer from the selected evidence. Best evidence:
- [p. 3] even an interpreter of dreams, since a dream also comes from Zeus, who can tell why Phoibos Apollo is so angry, if for the sake of some vow, some hecatomb he blames us, 65 if given the fragrant smoke of lambs, of he goats, somehow he can be...
- [p. 9] And if the everlasting gods have made him a spearman, 290 yet they have not given him the right to speak abusively.' Then looking at him darkly brilliant Achilleus answered him: 'So must I be called of no account and a coward if I must carr...
- [p. 15] 530 So these two who had made their plans separated, and Thetis leapt down again from shining Olympos into the sea's depth, but Zeus went back to his own house, and all the gods rose up from their chairs to greet the coming of their father,...
- [p. 16] Truly too much in time past I have not questioned nor probed you, but you are entirely free to think out whatever pleases you. Now, though, I am terribly afraid you were won over SSS by Thetis the silver-footed, the daughter of the sea's an...
- [p. 10] And Achilleus took no joy at all when he saw them. These two terrified and in awe of the king stood waiting quietly, and did not speak a word at all nor question him. But he knew the whole matter in his own heart, and spoke first: 'Welcome,...
Evidence:
- [p. 3 | p0003_full] even an interpreter of dreams, since a dream also comes from Zeus, who can tell why Phoibos Apollo is so angry, if for the sake of some vow, some hecatomb he blames us, 65 if given the fragrant smoke of lambs, of he goats, somehow he can be made willing to beat the bane aside from us.' He spoke thus and sat down again, and among them stood up Kalchas, Thestor's son, far the best of the bird interpreters, who knew all things that were, the things to come and the things past, 70 who guided into the land of Ilion the ships of the Achaians through that seercraft of his own that Phoibos Apollo gave him. He in kind intention toward all stood forth and addressed them: 'You have bidden me, Achilleus beloved of Zeus, to explain to you this anger of Apollo the lord who strikes from afar. Then 75 I will speak; yet make me a promise and swear before me readily by word and work of your hands to defend me, since I believe I shall make a man angry who holds great kingship over the men of Argos, and a...
- [p. 9 | p0009_full] And if the everlasting gods have made him a spearman, 290 yet they have not given him the right to speak abusively.' Then looking at him darkly brilliant Achilleus answered him: 'So must I be called of no account and a coward if I must carry out every order you may happen to give me. Tell other men to do these things, but give me no more 295 commands, since I for my part have no intention to obey you. And put away in your thoughts this other thing I tell you. With my hands I will not fight for the girl's sake, neither with you nor any other man, since you take her away who gave her.
- [p. 15 | p0015_full] 530 So these two who had made their plans separated, and Thetis leapt down again from shining Olympos into the sea's depth, but Zeus went back to his own house, and all the gods rose up from their chairs to greet the coming of their father, not one had courage to keep his place as the father advanced, but stood up to greet him. 535 Thus he took his place on the throne; yet Hera was not ignorant, having seen how he had been plotting counsels with Thetis the silver-footed, the daughter of the sea's ancient, and at once she spoke revilingly to Zeus son of Kronos: 'Treacherous one, what god has been plotting counsels with you? 540 Always it is dear to your heart in my absence to think of secret things and decide upon them. Never have you patience frankly to speak forth to me the thing that you purpose.' Then to her the father of gods and men made answer: 'Hera, do not go on hoping that you will hear all my 545 thoughts, since these will be too hard for you, though you are my wife. Any thou...
- [p. 16 | p0016_full] Truly too much in time past I have not questioned nor probed you, but you are entirely free to think out whatever pleases you. Now, though, I am terribly afraid you were won over SSS by Thetis the silver-footed, the daughter of the sea's ancient. For early in the morning she sat beside you and took your knees, and I think you bowed your head in assent to do honour to Achilleus, and to destroy many beside the ships of the Achaians.' Then in return Zeus who gathers the clouds made answer: 560 'Dear lady, I never escape you, you are always full of suspicion. Yet thus you can accomplish nothing surely, but be more distant from my heart than ever, and it will be the worse for you. If what you say is true, then that is the way I wish it.
- [p. 10 | iliad_book1_p0010_c01] And Achilleus took no joy at all when he saw them. These two terrified and in awe of the king stood waiting quietly, and did not speak a word at all nor question him. But he knew the whole matter in his own heart, and spoke first: 'Welcome, heralds, messengers of Zeus and of mortals.
Diagnostics:
- retrieval_backend: vector
- vector_succeeded: True
- llm_succeeded: True
- pages_before_rerank: [3, 16, 7, 15, 9, 10, 5, 8, 2, 14]
- pages_after_expansion: [3, 16, 3, 16, 16, 9, 15, 15, 9, 10, 4, 10]
- followup_queries: ['Kalchas fear reason', 'Apollo anger cause']
- pages_after_followup: [3, 16, 3, 16, 16, 9, 15, 15, 9, 10, 15, 4]
- evidence_sufficiency: {'sufficient': True, 'broad_question': False, 'cited_pages': [3, 9, 10, 15, 16], 'question_term_overlap': ['afraid', 'kalchas', 'speak'], 'reason': 'ok'}
```

### Evaluation

**Question:** Who is Kalchas, and why is he afraid to speak?  
**Expected evidence:** p. 3  
**Expected answer:** Kalchas is Thestor's son, a seer/bird-interpreter who knows Apollo's will/cause of Apollo's anger. He is afraid because his answer will anger Agamemnon, the powerful king; Achilles promises to protect him.

## v3 response assessed

The v3 answer does **not** synthesize an answer. It says:

> I could not produce a fully synthesized answer from the selected evidence. Best evidence:

It then lists p. 3 first, followed by irrelevant pages 9, 15, 16, and 10. The full p. 3 evidence block contains all necessary facts: Kalchas is “far the best of the bird interpreters,” has seercraft from Apollo, is asked to explain Apollo's anger, asks Achilles to defend him because he expects to anger a powerful king, and Achilles promises protection even against Agamemnon.

## Rubric scores

| Criterion | Score | Notes |
|---|---:|---|
| retrieval_relevance | 4/5 | Correct page p. 3 is top-ranked and the full evidence contains all required facts. However, reranking/selection still includes many irrelevant pages and duplicates. |
| citation_accuracy | 3/5 | The p. 3 citation directly supports a correct answer, but the remaining cited pages do not support this question. Since no real answer is synthesized, citation use is only partially successful. |
| speaker_attribution | n/a | No substantive synthesized claim is made, so there is no clear misattribution. |
| causal_chain | 1/5 | The necessary causal chain is present in p. 3 evidence, but the response itself does not state that Kalchas fears angering Agamemnon by revealing the cause of Apollo's anger. |
| no_hallucination | 5/5 | The response avoids invented claims and does not confuse Kalchas with Chryses. |
| answer_quality | 1/5 | It is an evidence dump/fallback, not a direct answer to a simple factual question. |

## Diagnosis

- **Retrieval:** Mostly successful. Page 3 is retrieved first and contains the exact answer. Follow-up queries also preserve p. 3. The main retrieval weakness is poor pruning: irrelevant pages 9, 10, 15, and 16 remain in the evidence list.
- **Reranking / evidence selection:** Mixed. It keeps the correct page, but duplicates p. 3 and admits weak distractors. Still, this should not have prevented a correct answer.
- **Generation:** Primary failure. Diagnostics say `llm_succeeded: True` and `evidence_sufficiency: sufficient`, yet the system emits the fallback “could not produce” message instead of synthesizing the obvious answer from p. 3.
- **OCR:** Not a blocker. `pages.json` p. 3 is readable and has the relevant lines cleanly.
- **Prompt / control logic:** Likely failure point. The answer-generation or confidence/fallback prompt appears too conservative or miswired: it marks evidence sufficient but still refuses synthesis.

## Brief comparison with v2

V2 gave a short synthesized sentence: “Kalchas is a seer who interprets the gods' will for the Danaans,” but omitted why he is afraid. V3 retrieves better/full p. 3 evidence, including the fear and Achilles' protection, but regresses in final answer quality by not synthesizing anything.

**Net:** v3 improves retrieval/evidence coverage over v2, but generation/control-flow is worse. For the user, v2 is slightly more useful because it at least answers “who,” while v3 only provides evidence despite having enough information for a complete answer.

## Correct answer reference

Kalchas is Thestor's son, a seer and bird-interpreter given prophetic skill by Apollo. He is afraid to speak because he knows his explanation of Apollo's anger will implicate and anger Agamemnon, a powerful king; Achilles therefore promises to protect him.

## Q3. Why does Apollo send a plague against the Achaians?

**Test set:** A — Simple factual lookup

### Expected

- Expected evidence: pp. 1–3

- Good answer should mention: Agamemnon dishonoured Chryses and refused to return Chryseis; Apollo punishes the army.

- Failure signs: Says Achilles caused the plague; cites only later Achilles/Agamemnon quarrel pages.

### Investigator response (v3 agentic)

```md
Question: Why does Apollo send a plague against the Achaians?
Response: I could not produce a fully synthesized answer from the selected evidence. Best evidence:
- [p. 3] For a king when he is angry with a man beneath him is too strong, 80 and suppose even for the day itself he swallow down his anger, he still keeps bitterness that remains until its fulfilment deep in his chest. Speak forth then, tell me if...
- [p. 2] so First he went after the mules and the circling hounds, then let go a tearing arrow against the men themselves and struck them. The corpse fires burned everywhere and did not stop burning. Nine days up and down the host ranged the god's a...
- [p. 11] We went against Thebe, the sacred city of Eëtion, and the city we sacked, and carried everything back to this place, and the sons of the Achaians made a fair distribution and for Atreus' son they chose out Chryseis of the fair cheeks. Then...
- [p. 13] And the men arranged the sacred hecatomb for the god in orderly fashion around the strong-founded altar. Next they washed their hands and took up the scattering barley. Standing among them with lifted arms Chryses prayed in a great voice: 4...
Evidence:
- [p. 3 | p0003_full] For a king when he is angry with a man beneath him is too strong, 80 and suppose even for the day itself he swallow down his anger, he still keeps bitterness that remains until its fulfilment deep in his chest. Speak forth then, tell me if you will protect me.' Then in answer again spoke Achilleus of the swift feet: 'Speak, interpreting whatever you know, and fear nothing. 85 In the name of Apollo beloved of Zeus to whom you, Kalchas, make your prayers when you interpret the gods' will to the Danaans, no man so long as I am alive above earth and see daylight shall lay the weight of his hands on you beside the hollow ships, not one of all the Danaans, even if you mean Agamemnon, 90 who now claims to be far the greatest of all the Achaians.' At this the blameless seer took courage again and spoke forth: 'No, it is not for the sake of some vow or hecatomb he blames us, but for the sake of his priest whom Agamemnon dishonoured and would not give him back his daughter nor accept the ransom....
- [p. 2 | p0002_full] so First he went after the mules and the circling hounds, then let go a tearing arrow against the men themselves and struck them. The corpse fires burned everywhere and did not stop burning. Nine days up and down the host ranged the god's arrows, but on the tenth Achilleus called the people to assembly; 55 a thing put into his mind by the goddess of the white arms, Hera, who had pity upon the Danaans when she saw them dying. Now when they were all assembled in one place together, Achilleus of the swift feet stood up among them and spoke forth: 'Son of Atreus, I believe now that straggling backwards 60 we must make our way home if we can even escape death, if fighting now must crush the Achaians and the plague likewise. No, come, let us ask some holy man, some prophet, [60 ]
- [p. 11 | p0011_full] We went against Thebe, the sacred city of Eëtion, and the city we sacked, and carried everything back to this place, and the sons of the Achaians made a fair distribution and for Atreus' son they chose out Chryseis of the fair cheeks. Then Chryses, priest of him who strikes from afar, Apollo, 370 came beside the fast ships of the bronze-armoured Achaians to ransom back his daughter, carrying gifts beyond count and holding in his hands wound on a staff of gold the ribbons of Apollo who strikes from afar, and supplicated all the Achaians, but above all Atreus' two sons, the marshals of the people. 375 Then all the rest of the Achaians cried out in favour that the priest be respected and the shining ransom be taken; yet this pleased not the heart of Atreus' son Agamemnon, but harshly he sent him away with a strong order upon him. The old man went back again in anger, but Apollo 380 listened to his prayer, since he was very dear to him, and let go the wicked arrow against the Argives.
- [p. 13 | p0013_full] And the men arranged the sacred hecatomb for the god in orderly fashion around the strong-founded altar. Next they washed their hands and took up the scattering barley. Standing among them with lifted arms Chryses prayed in a great voice: 450 'Hear me, lord of the silver bow, who set your power about Chryse and Killa the sacrosanct, who are lord in strength over Tenedos; if once before you listened to my prayers and did me honour and smote strongly the host of the Achaians, so one more time bring to pass the wish that I pray for. 455 Beat aside at last the shameful plague from the Danaans.' So he spoke in prayer, and Phoibos Apollo heard him. And when all had made prayer and flung down the scattering barley first they drew back the victims' heads and slaughtered them and skinned them, and cut away the meat from the thighs and wrapped them in fat, 460 making a double fold, and laid shreds of flesh upon them. The old man burned these on a cleft stick and poured the gleaming wine over, wh...
Diagnostics:
- retrieval_backend: vector
- vector_succeeded: True
- llm_succeeded: True
- pages_before_rerank: [3, 13, 2, 11, 1, 7, 16, 9, 10, 15]
- pages_after_expansion: [3, 3, 3, 2, 2, 2, 11, 13, 13, 11, 9, 12]
- followup_queries: ["Apollo's reason for sending plague to Achaians", "Agamemnon's action towards Apollo's priest"]
- pages_after_followup: [3, 3, 3, 2, 2, 2, 13, 11, 13, 11, 9, 12]
- evidence_sufficiency: {'sufficient': True, 'broad_question': False, 'cited_pages': [2, 3, 11, 13], 'question_term_overlap': ['achaians', 'against', 'apollo', 'plague', 'send'], 'reason': 'ok'}
```

### Evaluation

**Question:** Why does Apollo send a plague against the Achaians?  
**Expected pages:** pp. 1–3  
**Expected answer:** Apollo sends the plague because Agamemnon dishonoured Chryses, Apollo's priest, by refusing the ransom / refusing to return Chryseis; Apollo punishes the Achaian army.

## v3 result assessed

The v3 response does **not** give a synthesized answer. It says it "could not produce a fully synthesized answer" and falls back to a `Best evidence` list.

## Lightweight checks

- **Expected-page coverage:** Good/partial. v3 cites **p. 2** and **p. 3**, both expected and directly relevant. It misses **p. 1**, which concisely states the cause, but p. 3 fully supplies the explanation and p. 2 supplies the narrative sequence.
- **Direct answer:** Fail. The evidence contains the answer, but the response refuses/fails to state it plainly.
- **Completeness:** In the evidence, strong. The p. 3 citation explicitly says Apollo blames them for Agamemnon dishonouring his priest and refusing to return the daughter or accept ransom. The p. 2 citation shows Apollo's arrows/plague. In the response prose, absent.
- **Forbidden failure signs:** Pass. It does **not** blame Achilles and does **not** rely only on later quarrel pages.
- **Extra/weak evidence:** p. 11 is a useful later recap; p. 13 is mostly about ending the plague and is less useful for the cause.

## Source check

- **p. 2** gives the clearest action sequence: Agamemnon drives Chryses away; Chryses prays that Apollo's arrows make the Danaans pay; Apollo hears and strikes the camp.
- **p. 3** gives Kalchas' explicit explanation: Apollo is angry "for the sake of his priest whom Agamemnon dishonoured" and because Agamemnon "would not give him back his daughter nor accept the ransom."
- **p. 11** repeats the same causal summary later.

## Rubric

| Criterion | Score | Notes |
|---|---:|---|
| retrieval_relevance | 4/5 | Retrieves highly relevant p. 2 and p. 3, plus useful p. 11. Missing p. 1 and including p. 13 keep it from perfect. |
| citation_accuracy | 4/5 | The cited evidence directly supports the correct cause. p. 13 is weaker/secondary, but the key citations are accurate. |
| speaker_attribution | n/a | No substantive speaker attribution in the answer; no misattribution detected. |
| causal_chain | 3/5 | The evidence preserves the chain, but the response itself does not synthesize it. |
| no_hallucination | 5/5 | The fallback avoids unsupported claims. |
| answer_quality | 1/5 | For a simple factual lookup, an evidence-only fallback is not satisfactory despite having enough evidence to answer. |

## v2 comparison

v2 was **better as a user-facing answer**: it directly answered that Apollo sends the plague because Agamemnon dishonoured Chryses, Apollo's priest. However, v2 missed p. 2 and omitted the explicit refusal-to-return-Chryseis / accept-ransom detail.

v3 is **better in retrieval/evidence coverage** because it includes p. 2 and a fuller p. 3 span with the decisive explanation. But v3 regresses in generation: it falls back instead of producing the obvious answer.

## Qwen strictness / fallback note

Diagnostics say `llm_succeeded: True` and `evidence_sufficiency: sufficient=True`, so this looks like an overly strict synthesis/validation fallback rather than an evidence failure. Qwen/v3 had enough grounded text to answer safely, but the strict fallback converted a good evidence set into an unsatisfactory final response.

## Overall judgment

**Partially successful but user-facing failure.** Retrieval is strong enough to answer Q3 correctly, and the evidence avoids the known failure signs. The final response should simply have said: Apollo sends the plague because Agamemnon dishonoured Chryses, Apollo's priest, by refusing the ransom and refusing to return Chryseis; Apollo punishes the Achaians in response.

## Q4. Who asks Thetis to appeal to Zeus, and what does he want Zeus to do?

**Test set:** B — Speaker/action attribution

### Expected

- Expected evidence: pp. 11–12

- Good answer should mention: Achilles asks Thetis; he wants Zeus to help the Trojans and push the Achaians back so Agamemnon realizes his mistake.

- Failure signs: Says Thetis asks Achilles; says Achilles directly prays to Zeus; misses the purpose of punishing the Achaians.

### Investigator response (v3 agentic)

```md
Question: Who asks Thetis to appeal to Zeus, and what does he want Zeus to do?
Response: sos Now give honour to my son short-lived beyond all other mortals." She wants Zeus to honor her son Achilles.
Evidence:
- [p. 14 | p0014_full] Afterwards they scattered to their own ships and their shelters. But that other still sat in anger beside his swift ships, Peleus' son divinely born, Achilleus of the swift feet. Never now would he go to assemblies where men win glory, 490 never more into battle, but continued to waste his heart out sitting there, though he longed always for the clamour and fighting. But when the twelfth dawn after this day appeared, the gods who live forever came back to Olympos all in a body and Zeus led them; nor did Thetis forget the entreaties 495 of her son, but she emerged from the sea's waves early in the morning and went up to the tall sky and Olympos. She found Kronos' broad-browed son apart from the others sitting upon the highest peak of rugged Olympos. goo She came and sat beside him with her left hand embracing his knees, but took him underneath the chin with her right hand and spoke in supplication to lord Zeus son of Kronos: 'Father Zeus, if ever before in word or action I did you favou...
- [p. 15 | p0015_full] I will look to these things that they be accomplished. See then, I will bend my head that you may believe me. For this among the immortal gods is the mightiest witness 525 I can give, and nothing I do shall be vain nor revocable nor a thing unfulfilled when I bend my head in assent to it.' He spoke, the son of Kronos, and nodded his head with the dark brows, and the immortally anointed hair of the great god swept from his divine head, and all Olympos was shaken. 530 So these two who had made their plans separated, and Thetis leapt down again from shining Olympos into the sea's depth, but Zeus went back to his own house, and all the gods rose up from their chairs to greet the coming of their father, not one had courage to keep his place as the father advanced, but stood up to greet him. 535 Thus he took his place on the throne; yet Hera was not ignorant, having seen how he had been plotting counsels with Thetis the silver-footed, the daughter of the sea's ancient, and at once she spoke...
- [p. 4 | p0004_full] Find me then some prize that shall be my own, lest I only among the Argives go without, since that were unfitting; 120 you are all witnesses to this thing, that my prize goes elsewhere.' Then in answer again spoke brilliant swift-footed Achilleus: 'Son of Atreus, most lordly, greediest for gain of all men, how shall the great-hearted Achaians give you a prize now? There is no great store of things lying about I know of. I25 But what we took from the cities by storm has been distributed; it is unbecoming for the people to call back things once given. No, for the present give the girl back to the god; we Achaians thrice and four times over will repay you, if ever Zeus gives into our hands the strong-walled citadel of Troy to be plundered.' I30 Then in answer again spoke powerful Agamemnon: 'Not that way, good fighter though you be, godlike Achilleus, strive to cheat, for you will not deceive, you will not persuade me. What do you want? To keep your own prize and have me sit here lacking...
Diagnostics:
- retrieval_backend: vector
- vector_succeeded: True
- llm_succeeded: True
- pages_before_rerank: [5, 7, 8, 14, 3, 9, 4, 16, 15, 6]
- pages_after_expansion: [4, 14, 15, 16, 14, 4, 16, 15, 14, 15, 16, 5]
- followup_queries: ['Thetis appeal Zeus evidence', 'Peleus son ask Thetis appeal Zeus']
- pages_after_followup: [4, 4, 14, 15, 16, 14, 16, 15, 14, 15, 16, 6]
- evidence_sufficiency: {'sufficient': True, 'broad_question': False, 'cited_pages': [4, 14, 15], 'question_term_overlap': ['thetis', 'want', 'zeus'], 'reason': 'ok'}
```

### Evaluation

**Question:** Who asks Thetis to appeal to Zeus, and what does he want Zeus to do?  
**Expected pages:** pp. 11–12  
**Expected answer:** Achilles asks his mother Thetis to appeal to Zeus. He wants Zeus to help the Trojans and pin/drive the Achaians back against their ships so Agamemnon realizes he dishonored Achilles.

## v3 response assessed

> sos Now give honour to my son short-lived beyond all other mortals." She wants Zeus to honor her son Achilles.

Evidence cited: p. 14, p. 15, p. 4.

## Source check

- **p. 11** directly answers the first half: Achilles tells Thetis, “protect your own son, going to Olympos and supplicating Zeus.”
- **p. 12** directly answers the second half: Achilles asks her to seek Zeus’ help for the Trojans and to pin the Achaians back against the ships/water so Agamemnon recognizes his madness and dishonor of Achilles.
- **p. 14** is later follow-through: Thetis appeals to Zeus and asks him to honor Achilles by strengthening the Trojans until the Achaians restore Achilles’ honor. This is related but secondary for Q4 because it is Thetis’ later execution of Achilles’ request, not Achilles asking her.
- **p. 15** is Zeus’ assent/aftermath and does not identify who asked Thetis.
- **p. 4** is unrelated quarrel/Chryseis-prize context.

## Rubric scores

| Criterion | Score | Notes |
|---|---:|---|
| retrieval_relevance | 2/5 | Retrieves related p. 14–15 but misses the required pp. 11–12 entirely; p. 4 is noise. |
| citation_accuracy | 2/5 | p. 14 supports Thetis asking Zeus to honor Achilles, but not the question’s key attribution: Achilles asks Thetis. p. 15 is secondary; p. 4 irrelevant. |
| speaker_attribution | 1/5 | The answer centers “She”/Thetis as requester to Zeus and never states Achilles asks Thetis. |
| causal_chain | 2/5 | It captures “honor Achilles” but omits Zeus helping Trojans, driving Achaians back, and Agamemnon recognizing his mistake. |
| no_hallucination | 3/5 | The Thetis-to-Zeus claim is source-grounded, but it is the wrong relation for this question and includes OCR artifact `sos`. |
| answer_quality | 1/5 | Not a direct answer to “Who asks Thetis”; incomplete and misleading despite a relevant partial fact. |

## Retrieval diagnostics

- Backend succeeded: `retrieval_backend: vector`, `vector_succeeded: True`, `llm_succeeded: True`.
- Initial retrieval did **not** include pp. 11–12: `pages_before_rerank: [5, 7, 8, 14, 3, 9, 4, 16, 15, 6]`.
- Expansion/follow-up still failed to recover the answer pages and repeatedly cycled around pp. 14–16 and p. 4.
- Follow-up queries were promising (`Thetis appeal Zeus evidence`, `Peleus son ask Thetis appeal Zeus`) but still missed the literal Achilles request on pp. 11–12.
- The sufficiency check is a false positive: `sufficient: True` based on overlap with “thetis,” “want,” and “zeus,” even though the cited pages lack the crucial “Achilles asks Thetis” span.

## Generation strictness

Generation stayed mostly within retrieved evidence, but it was not strict enough about the question’s role structure. It answered the adjacent event “What does Thetis ask Zeus?” rather than “Who asks Thetis to appeal to Zeus?” It should either have refused/flagged insufficient evidence or stated only that the retrieved evidence shows Thetis later appealed on her son’s behalf. The inclusion of the OCR artifact `sos` in the response also suggests weak cleanup/quotation discipline.

## Brief comparison with v2

v2 answered: “Thetis asks Zeus for help on p.” and cited p. 3, p. 14, p. 15. v3 is slightly better in that it extracts a real p. 14 request—Zeus should honor Achilles—but it remains a failure for Q4. Both versions miss pp. 11–12 and both miscenter Thetis’ later appeal instead of Achilles’ request to Thetis. v3 improves partial content but not the core speaker/action attribution or causal purpose.

## Overall judgment

**Failed / inadequate.** v3 retrieves secondary follow-through evidence but misses the decisive pages and gives the wrong attribution. Correct answer: **Achilles asks Thetis to appeal to Zeus; he wants Zeus to help the Trojans drive the Achaians back to their ships so Agamemnon realizes he dishonored Achilles.**

## Q5. What does Thetis ask Zeus to do for Achilles?

**Test set:** B — Speaker/action attribution

### Expected

- Expected evidence: pp. 14–15

- Good answer should mention: Thetis asks Zeus to honour Achilles by giving strength to the Trojans until the Achaians restore Achilles’ honour.

- Failure signs: Says Thetis asks Zeus to return Briseis; says Zeus helps Achilles fight directly.

### Investigator response (v3 agentic)

```md
Question: What does Thetis ask Zeus to do for Achilles?
Response: I could not produce a fully synthesized answer from the selected evidence. Best evidence:
- [p. 14] Afterwards they scattered to their own ships and their shelters. But that other still sat in anger beside his swift ships, Peleus' son divinely born, Achilleus of the swift feet. Never now would he go to assemblies where men win glory, 490...
- [p. 15] I will look to these things that they be accomplished. See then, I will bend my head that you may believe me. For this among the immortal gods is the mightiest witness 525 I can give, and nothing I do shall be vain nor revocable nor a thing...
- [p. 4] I25 But what we took from the cities by storm has been distributed; it is unbecoming for the people to call back things once given. No, for the present give the girl back to the god; we Achaians thrice and four times over will repay you, if...
Evidence:
- [p. 14 | p0014_full] Afterwards they scattered to their own ships and their shelters. But that other still sat in anger beside his swift ships, Peleus' son divinely born, Achilleus of the swift feet. Never now would he go to assemblies where men win glory, 490 never more into battle, but continued to waste his heart out sitting there, though he longed always for the clamour and fighting. But when the twelfth dawn after this day appeared, the gods who live forever came back to Olympos all in a body and Zeus led them; nor did Thetis forget the entreaties 495 of her son, but she emerged from the sea's waves early in the morning and went up to the tall sky and Olympos. She found Kronos' broad-browed son apart from the others sitting upon the highest peak of rugged Olympos. goo She came and sat beside him with her left hand embracing his knees, but took him underneath the chin with her right hand and spoke in supplication to lord Zeus son of Kronos: 'Father Zeus, if ever before in word or action I did you favou...
- [p. 15 | p0015_full] I will look to these things that they be accomplished. See then, I will bend my head that you may believe me. For this among the immortal gods is the mightiest witness 525 I can give, and nothing I do shall be vain nor revocable nor a thing unfulfilled when I bend my head in assent to it.' He spoke, the son of Kronos, and nodded his head with the dark brows, and the immortally anointed hair of the great god swept from his divine head, and all Olympos was shaken. 530 So these two who had made their plans separated, and Thetis leapt down again from shining Olympos into the sea's depth, but Zeus went back to his own house, and all the gods rose up from their chairs to greet the coming of their father, not one had courage to keep his place as the father advanced, but stood up to greet him. 535 Thus he took his place on the throne; yet Hera was not ignorant, having seen how he had been plotting counsels with Thetis the silver-footed, the daughter of the sea's ancient, and at once she spoke...
- [p. 4 | iliad_book1_p0004_c01] I25 But what we took from the cities by storm has been distributed; it is unbecoming for the people to call back things once given. No, for the present give the girl back to the god; we Achaians thrice and four times over will repay you, if ever Zeus gives into our hands the strong-walled citadel of Troy to be plundered.' I30 Then in answer again spoke powerful Agamemnon: 'Not that way, good fighter though you be, godlike Achilleus, strive to cheat, for you will not deceive, you will not persuade me. What do you want?
Diagnostics:
- retrieval_backend: vector
- vector_succeeded: True
- llm_succeeded: True
- pages_before_rerank: [14, 7, 4, 13, 5, 16, 3, 15, 8, 9]
- pages_after_expansion: [14, 14, 14, 15, 16, 16, 15, 15, 16, 7, 7, 4]
- followup_queries: ['Thetis asks Zeus to do for Achilles', "Zeus grants Thetis' request for Achilles"]
- pages_after_followup: [14, 14, 14, 15, 16, 16, 15, 15, 16, 4, 7, 1]
- evidence_sufficiency: {'sufficient': True, 'broad_question': False, 'cited_pages': [4, 14, 15], 'question_term_overlap': ['ask', 'thetis', 'zeus'], 'reason': 'ok'}
```

### Evaluation

**Question:** What does Thetis ask Zeus to do for Achilles?  
**Expected pages:** pp. 14–15  
**Expected answer:** Thetis asks Zeus to honor Achilles by giving strength to the Trojans until the Achaians restore/increase Achilles' rights and honor.

## v3 response assessed

The v3 response does **not** answer the question. It says it "could not produce a fully synthesized answer" and then lists best evidence from p. 14, p. 15, and p. 4.

## Source check

Page 14 contains the decisive request:

> "Now give honour to my son... Zeus of the counsels, lord of Olympos, now do him honour. So long put strength into the Trojans, until the Achaians give my son his rights, and his honour is increased among them."

Page 15 confirms Zeus accepts by nodding assent and saying he will accomplish it.

## Lightweight checks

- **Expected-page coverage:** Partial/good. v3 retrieves p. 14 and p. 15, the expected page range.
- **Core answer present in response:** Fail. The final response never states that Thetis asks Zeus to strengthen the Trojans until the Achaians restore Achilles' honor.
- **Full-page expansion:** Mixed/mostly not fixed at the user-visible level. Diagnostics show `p0014_full`, so expansion reached the right full page, but the displayed p. 14 evidence is truncated before the crucial request span. If the LLM had the full page internally, this becomes a synthesis/generation failure; as rendered to the user, the p. 14 request span still is not exposed.
- **Irrelevant evidence:** p. 4 is noise for this question.
- **Forbidden failure signs:** Pass. It does not say Thetis asks Zeus to return Briseis and does not say Zeus helps Achilles fight directly.

## Rubric scores

| Criterion | Score | Notes |
|---|---:|---|
| retrieval_relevance | 3/5 | Finds expected pp. 14–15 and uses `p0014_full`, but the visible evidence omits the decisive p. 14 lines and includes irrelevant p. 4. |
| citation_accuracy | 2/5 | Citations are real, but the response makes no supported answer claim; visible p. 14/p. 15 snippets only partially frame the request/acceptance. |
| speaker_attribution | 2/5 | It correctly locates Thetis/Zeus context but never attributes the actual request. |
| causal_chain | 1/5 | Misses the chain: Achilles dishonored → Thetis asks Zeus to honor him → Trojans strengthened until Achaians restore honor. |
| no_hallucination | 4/5 | Avoids the major wrong-answer failure signs, though the inability claim is misleading because the source contains the answer. |
| answer_quality | 1/5 | Not useful as an answer; it falls back to evidence snippets despite sufficient source context. |

## Brief comparison with v2

- **v2:** Retrieved p. 14–15 but selected a p. 14 chunk that stopped before the answer, then incorrectly claimed the evidence did not specify the entreaties.
- **v3:** Improves retrieval metadata by expanding to `p0014_full` and avoids the stronger false claim that the text does not specify the answer. However, it still fails to synthesize the answer and the rendered evidence still does not show the crucial p. 14 request span.

## Overall judgment

**Failed / near miss.** v3 finds the right page range and likely improves backend context through full-page expansion, but it does not fix the final user-facing answer for Q5. The correct answer should be: **Thetis asks Zeus to honor Achilles by giving strength to the Trojans until the Achaians give Achilles his rights and increase his honor.**

## Q6. What does Hera suspect Zeus has done?

**Test set:** B — Speaker/action attribution

### Expected

- Expected evidence: p. 16

- Good answer should mention: Hera suspects Zeus was persuaded by Thetis to honour Achilles and harm the Achaians.

- Failure signs: Attributes Hera’s suspicion to Achilles; says Achilles criticizes Zeus.

### Investigator response (v3 agentic)

```md
Question: What does Hera suspect Zeus has done?
Response: I could not produce a fully synthesized answer from the selected evidence. Best evidence:
- [p. 15] or else refuse it, you have nothing to fear, that I may know 515 by how much I am the most dishonoured of all gods.' Deeply disturbed Zeus who gathers the clouds answered her: 'This is a disastrous matter when you set me in conflict with He...
- [p. 16] For early in the morning she sat beside you and took your knees, and I think you bowed your head in assent to do honour to Achilleus, and to destroy many beside the ships of the Achaians.' Then in return Zeus who gathers the clouds made ans...
- [p. 6] So he spoke. And the anger came on Peleus' son, and within his shaggy breast the heart was divided two ways, pondering 190 whether to draw from beside his thigh the sharp sword, driving away all those who stood between and kill the son of A...
Evidence:
- [p. 15 | p0015_full] or else refuse it, you have nothing to fear, that I may know 515 by how much I am the most dishonoured of all gods.' Deeply disturbed Zeus who gathers the clouds answered her: 'This is a disastrous matter when you set me in conflict with Hera, and she troubles me with recriminations. Since even as things are, forever among the immortals 520 she is at me and speaks of how I help the Trojans in battle. Even so, go back again now, go away, for fear she see us. I will look to these things that they be accomplished.
- [p. 16 | p0016_full] For early in the morning she sat beside you and took your knees, and I think you bowed your head in assent to do honour to Achilleus, and to destroy many beside the ships of the Achaians.' Then in return Zeus who gathers the clouds made answer: 560 'Dear lady, I never escape you, you are always full of suspicion. Yet thus you can accomplish nothing surely, but be more distant from my heart than ever, and it will be the worse for you. If what you say is true, then that is the way I wish it. 565 But go then, sit down in silence, and do as I tell you, for fear all the gods, as many as are on Olympos, can do nothing if I come close and lay my unconquerable hands upon you.' He spoke, and the goddcss the ox-eyed lady Hera was frightened and went and sat down in silence wrenching her heart to obedience, 57o and all the Uranian gods in the house of Zeus werc troubled. Hephaistos the renowned smith rose up to speak among them, to bring comfort to his beloved mother, Hera of the white arms: 'Thi...
- [p. 6 | p0006_full] So he spoke. And the anger came on Peleus' son, and within his shaggy breast the heart was divided two ways, pondering 190 whether to draw from beside his thigh the sharp sword, driving away all those who stood between and kill the son of Atreus, or else to check the spleen within and keep down his anger. Now as he weighed in mind and spirit these two courses and was drawing from its scabbard the great sword, Athene descended 195 from the sky. For Hera the goddess of the white arms sent her, who loved both men equally in her heart and cared for them. The goddess standing behind Peleus' son caught him by the fair hair, appearing to him only, for no man of the others saw her. Achilleus in amazement turned about, and straightway 200 knew Pallas Athene and the terrible eyes shining. He uttered winged words and addressed her: 'Why have you come now, o child of Zeus of the aegis, once more?
Diagnostics:
- retrieval_backend: vector
- vector_succeeded: True
- llm_succeeded: True
- pages_before_rerank: [3, 15, 16, 4, 13, 7, 14, 1, 9, 11]
- pages_after_expansion: [11, 15, 16, 15, 16, 11, 15, 16, 17, 3, 3, 4]
- followup_queries: ['Hera suspicion Zeus evidence', 'Zeus actions Hera p16']
- pages_after_followup: [6, 15, 6, 16, 11, 5, 11, 15, 16, 15, 16, 17]
- evidence_sufficiency: {'sufficient': True, 'broad_question': False, 'cited_pages': [6, 15, 16], 'question_term_overlap': ['hera', 'zeus'], 'reason': 'ok'}
```

### Evaluation

**Verdict:** Retrieval improved; answer synthesis failed. v3 retrieves the decisive p. 16 passage where Hera says Zeus was won over by Thetis, nodded assent to honour Achilles, and will destroy many beside the Achaian ships. The final response falls back to evidence instead of stating the answer.

| Metric | Score | Notes |
|---|---:|---|
| retrieval_relevance | 4/5 | Final evidence includes p. 16 and p. 15 setup; p. 6 is noise. |
| citation_accuracy | 4/5 | p. 16 directly supports the expected answer. |
| speaker_attribution | n/a | No synthesized speaker claim; evidence itself identifies Hera/Zeus. |
| causal_chain | 3/5 | Evidence has Thetis -> Zeus assent -> honour Achilles/harm Achaians, but response does not synthesize. |
| no_hallucination | 5/5 | Fallback avoids invented claims. |
| answer_quality | 1/5 | Evidence-only despite sufficient evidence. |

**Delta vs v2:** v2 gave a partial answer from p. 15 but missed p. 16. v3 is better retrieval-wise and worse user-facing because it refuses synthesis. This is a Qwen/validation strictness issue, not an evidence issue.

## Q7. Trace the chain of events from Chryses’ request to Achilles’ withdrawal from the fighting.

**Test set:** C — Cause-and-effect chain

### Expected

- Expected evidence: pp. 1–12

- Good answer should mention: 1. Chryses asks for daughter back. 2. Agamemnon refuses. 3. Apollo sends plague. 4. Kalchas explains cause. 5. Agamemnon demands compensation. 6. Agamemnon takes Briseis. 7. Achilles withdraws and appeals to Thetis.

- Failure signs: Skips Kalchas; skips Briseis; treats Achilles’ withdrawal as random anger.

### Investigator response (v3 agentic)

```md
Question: Trace the chain of events from Chryses’ request to Achilles’ withdrawal from the fighting.
Response: I could not produce a fully synthesized answer from the selected evidence. Best evidence:
- [p. 11] We went against Thebe, the sacred city of Eëtion, and the city we sacked, and carried everything back to this place, and the sons of the Achaians made a fair distribution and for Atreus' son they chose out Chryseis of the fair cheeks. Then...
- [p. 2] so First he went after the mules and the circling hounds, then let go a tearing arrow against the men themselves and struck them. The corpse fires burned everywhere and did not stop burning. Nine days up and down the host ranged the god's a...
- [p. 8] Do you also obey, since to be persuaded is better. You, great man that you are, yet do not take the girl away 275 but let her be, a prize as the sons of the Achaians gave her first. Nor, son of Peleus, think to match your strength with the...
- [p. 9] Then they accomplished perfect hecatombs to Apollo, 315 of bulls and goats along the beach of the barren salt sea. The savour of the burning swept in circles up to the bright sky. Thus these were busy about the army. But Agamemnon did not g...
- [p. 10] Yet let them be witnesses in the sight of the blessed gods, in the sight of mortal men, and of this cruel king, if ever hereafter 340 there shall be need of me to beat back the shameful destruction from the rest. For surely in ruinous heart...
Evidence:
- [p. 11 | p0011_full] We went against Thebe, the sacred city of Eëtion, and the city we sacked, and carried everything back to this place, and the sons of the Achaians made a fair distribution and for Atreus' son they chose out Chryseis of the fair cheeks. Then Chryses, priest of him who strikes from afar, Apollo, 370 came beside the fast ships of the bronze-armoured Achaians to ransom back his daughter, carrying gifts beyond count and holding in his hands wound on a staff of gold the ribbons of Apollo who strikes from afar, and supplicated all the Achaians, but above all Atreus' two sons, the marshals of the people. 375 Then all the rest of the Achaians cried out in favour that the priest be respected and the shining ransom be taken; yet this pleased not the heart of Atreus' son Agamemnon, but harshly he sent him away with a strong order upon him. The old man went back again in anger, but Apollo 380 listened to his prayer, since he was very dear to him, and let go the wicked arrow against the Argives. And...
- [p. 2 | p0002_full] so First he went after the mules and the circling hounds, then let go a tearing arrow against the men themselves and struck them. The corpse fires burned everywhere and did not stop burning. Nine days up and down the host ranged the god's arrows, but on the tenth Achilleus called the people to assembly; 55 a thing put into his mind by the goddess of the white arms, Hera, who had pity upon the Danaans when she saw them dying. Now when they were all assembled in one place together, Achilleus of the swift feet stood up among them and spoke forth: 'Son of Atreus, I believe now that straggling backwards 60 we must make our way home if we can even escape death, if fighting now must crush the Achaians and the plague likewise. No, come, let us ask some holy man, some prophet, [60 ]
- [p. 8 | p0008_full] Do you also obey, since to be persuaded is better. You, great man that you are, yet do not take the girl away 275 but let her be, a prize as the sons of the Achaians gave her first. Nor, son of Peleus, think to match your strength with the king, since never equal with the rest is the portion of honour of the sceptred king to whom Zeus gives magnificence. Even 280 though you are the stronger man, and the mother who bore you was immortal, yet is this man greater who is lord over more than you rule: Son of Atreus, give up your anger; even I entreat you to give over your bitterness against Achilleus, he who stands as a great bulwark of battle over all the Achaians.' Then in answer again spoke powerful Agamemnon: 285 'Yes, old sir, all this you have said is fair and orderly. Yet here is a man who wishes to be above all others, who wishes to hold power over all, and to be lord of all, and give them their orders, yet I think one will not obey him. [66]
- [p. 9 | p0009_full] Then they accomplished perfect hecatombs to Apollo, 315 of bulls and goats along the beach of the barren salt sea. The savour of the burning swept in circles up to the bright sky. Thus these were busy about the army. But Agamemnon did not give up his anger and the first threat he made to Achilleus, but to Talthybios he gave his orders and Eurybates 320 who were heralds and hard-working henchmen to him: 'Go now to the shelter of Peleus' son Achilleus, to bring back Briseis of the fair cheeks leading her by the hand. And if he will not give her, I must come in person to take her with many men behind me, and it will be the worse for him.' 325 He spoke and sent them forth with this strong order upon them. They went against their will beside the beach of the barren [67]
- [p. 10 | p0010_adjacent] Yet let them be witnesses in the sight of the blessed gods, in the sight of mortal men, and of this cruel king, if ever hereafter 340 there shall be need of me to beat back the shameful destruction from the rest. For surely in ruinous heart he makes sacrifice and has not wit enough to look behind and before him that the Achaians fighting beside their ships shall not perish.' So he spoke, and Patroklos obeyed his beloved companion. 345 He led forth from the hut Briseis of the fair cheeks and gave her to be taken away; and they walked back beside the ships of the Achaians, and the woman all unwilling went with them still.
Diagnostics:
- retrieval_backend: vector
- vector_succeeded: True
- llm_succeeded: True
- pages_before_rerank: [5, 9, 2, 16, 6, 4, 7, 11, 13, 15, 8, 1]
- pages_after_expansion: [11, 11, 9, 9, 9, 10, 2, 8, 2, 8, 6, 8]
- followup_queries: ['Achilles withdrawal from fighting after Chryses request', "Apollo's arrow plague aftermath Achilleus assembly"]
- pages_after_followup: [11, 11, 9, 9, 9, 10, 2, 8, 2, 8, 6, 8]
- evidence_sufficiency: {'sufficient': True, 'broad_question': True, 'cited_pages': [2, 8, 9, 10, 11], 'question_term_overlap': ['chryses', 'fighting'], 'reason': 'ok'}
```

### Evaluation

**Verdict:** Retrieval coverage improves substantially, but the answer is still evidence-only. v3 retrieves p. 11 recap, p. 2 plague/assembly, p. 8 Nestor, p. 9 Briseis order, and p. 10 Briseis taken/Achilles withdrawal context. It still misses a clean generated ordered chain.

| Metric | Score | Notes |
|---|---:|---|
| retrieval_relevance | 4/5 | Covers most required chain via pp. 2, 8, 9, 10, 11; p. 3/Kalchas is less explicit in final evidence. |
| citation_accuracy | 4/5 | Citations support key events. |
| speaker_attribution | n/a | No synthesized claims. |
| causal_chain | 3/5 | Evidence preserves much of sequence, but answer does not trace it. |
| no_hallucination | 5/5 | No Chryseis/Briseis hallucination like v2. |
| answer_quality | 1/5 | Fails requested chain format. |

**Delta vs v2:** v3 is much safer than v2, which confused Chryses' daughter with Briseis. Retrieval is stronger; generation strictness/fallback is now the bottleneck.

## Q8. How does the quarrel between Achilles and Agamemnon move from a dispute over Chryseis to a dispute over Briseis?

**Test set:** C — Cause-and-effect chain

### Expected

- Expected evidence: pp. 3–10

- Good answer should mention: Agamemnon must return Chryseis but demands another prize; he threatens/takes Briseis from Achilles as compensation.

- Failure signs: Says Briseis belongs to Agamemnon originally; says Achilles takes Chryseis.

### Investigator response (v3 agentic)

```md
Question: How does the quarrel between Achilles and Agamemnon move from a dispute over Chryseis to a dispute over Briseis?
Response: I could not produce a fully synthesized answer from the selected evidence. Best evidence:
- [p. 8] Nor, son of Peleus, think to match your strength with the king, since never equal with the rest is the portion of honour of the sceptred king to whom Zeus gives magnificence. Even 280 though you are the stronger man, and the mother who bore...
- [p. 9] Then they accomplished perfect hecatombs to Apollo, 315 of bulls and goats along the beach of the barren salt sea. The savour of the burning swept in circles up to the bright sky. Thus these were busy about the army. But Agamemnon did not g...
- [p. 3] Then 75 I will speak; yet make me a promise and swear before me readily by word and work of your hands to defend me, since I believe I shall make a man angry who holds great kingship over the men of Argos, and all the Achaians obey him. For...
- [p. 10] Draw near. You are not to blame in my sight, but Agamemnon 335 who sent the two of you here for the sake of the girl Briseis. Go then, illustrious Patroklos, and bring the girl forth and give her to these to be taken away.
- [p. 12] These when they were inside the many-hollowed harbour took down and gathered together the sails and stowed them in the black ship, let down mast by the forestays, and settled it into the mast crutch 435 easily, and rowed her in with oars to...
Evidence:
- [p. 8 | iliad_book1_p0008_c01] Nor, son of Peleus, think to match your strength with the king, since never equal with the rest is the portion of honour of the sceptred king to whom Zeus gives magnificence. Even 280 though you are the stronger man, and the mother who bore you was immortal, yet is this man greater who is lord over more than you rule: Son of Atreus, give up your anger; even I entreat you to give over your bitterness against Achilleus, he who stands as a great bulwark of battle over all the Achaians.' Then in answer again spoke powerful Agamemnon: 285 'Yes, old sir, all this you have said is fair and orderly. Yet here is a man who wishes to be above all others, who wishes to hold power over all, and to be lord of all, and give them their orders, yet I think one will not obey him.
- [p. 9 | p0009_full] Then they accomplished perfect hecatombs to Apollo, 315 of bulls and goats along the beach of the barren salt sea. The savour of the burning swept in circles up to the bright sky. Thus these were busy about the army. But Agamemnon did not give up his anger and the first threat he made to Achilleus, but to Talthybios he gave his orders and Eurybates 320 who were heralds and hard-working henchmen to him: 'Go now to the shelter of Peleus' son Achilleus, to bring back Briseis of the fair cheeks leading her by the hand. And if he will not give her, I must come in person to take her with many men behind me, and it will be the worse for him.' 325 He spoke and sent them forth with this strong order upon them. They went against their will beside the beach of the barren [67]
- [p. 3 | p0003_full] Then 75 I will speak; yet make me a promise and swear before me readily by word and work of your hands to defend me, since I believe I shall make a man angry who holds great kingship over the men of Argos, and all the Achaians obey him. For a king when he is angry with a man beneath him is too strong, 80 and suppose even for the day itself he swallow down his anger, he still keeps bitterness that remains until its fulfilment deep in his chest. Speak forth then, tell me if you will protect me.' Then in answer again spoke Achilleus of the swift feet: 'Speak, interpreting whatever you know, and fear nothing. 85 In the name of Apollo beloved of Zeus to whom you, Kalchas, make your prayers when you interpret the gods' will to the Danaans, no man so long as I am alive above earth and see daylight shall lay the weight of his hands on you beside the hollow ships, not one of all the Danaans, even if you mean Agamemnon, 90 who now claims to be far the greatest of all the Achaians.' At this the b...
- [p. 10 | p0010_adjacent] Draw near. You are not to blame in my sight, but Agamemnon 335 who sent the two of you here for the sake of the girl Briseis. Go then, illustrious Patroklos, and bring the girl forth and give her to these to be taken away.
- [p. 12 | p0012_adjacent] These when they were inside the many-hollowed harbour took down and gathered together the sails and stowed them in the black ship, let down mast by the forestays, and settled it into the mast crutch 435 easily, and rowed her in with oars to the mooring. They threw over the anchor stones and made fast the stern cables and themselves stepped out on to the break of the sea beach, and led forth the hecatomb to the archer Apollo, and Chryseis herself stepped forth from the sea-going vessel. 440 Odysseus of the many designs guided her to the altar [70]
Diagnostics:
- retrieval_backend: vector
- vector_succeeded: True
- llm_succeeded: True
- pages_before_rerank: [7, 6, 1, 3, 8, 5, 16, 4, 9, 11, 15, 14]
- pages_after_expansion: [9, 9, 11, 11, 6, 6, 3, 3, 10, 5, 12, 8]
- followup_queries: ['quarrel between Achilles and Agamemnon over Chryseis and Briseis', 'move from dispute over Chryseis to Briseis in Iliad']
- pages_after_followup: [9, 9, 11, 11, 6, 6, 3, 3, 10, 5, 12, 8]
- evidence_sufficiency: {'sufficient': True, 'broad_question': True, 'cited_pages': [3, 8, 9, 10, 12], 'question_term_overlap': ['agamemnon', 'briseis', 'chryseis', 'over'], 'reason': 'ok'}
```

### Evaluation

**Verdict:** Retrieval is much better than v2 and avoids the Chryseis/Briseis hallucination, but final answer is fallback evidence. Evidence includes p. 3 background, p. 9 order to take Briseis, p. 10 actual handoff, and p. 12 Chryseis return; p. 4/p. 6 transition logic is still not strongly exposed in final evidence.

| Metric | Score | Notes |
|---|---:|---|
| retrieval_relevance | 3/5 | Good endpoint evidence for Briseis; missing strongest pp. 4 and 6 transition passages. |
| citation_accuracy | 4/5 | Evidence is page-correct and relevant. |
| speaker_attribution | n/a | No synthesized speaker claims. |
| causal_chain | 2/5 | Evidence fragments show parts, but not full compensation-prize chain. |
| no_hallucination | 5/5 | Avoids v2's false claim that Chryses' daughter is Briseis. |
| answer_quality | 1/5 | Evidence-only; no answer. |

**Delta vs v2:** Clear improvement in safety and retrieval. Still needs an answer synthesis pass that can form: return Chryseis -> demand replacement prize -> take Briseis.

## Q9. Why does Achilles believe Agamemnon has dishonoured him?

**Test set:** C — Cause-and-effect chain

### Expected

- Expected evidence: pp. 5–12

- Good answer should mention: Achilles fights for Agamemnon/Menelaos’ cause, yet Agamemnon takes his prize; Briseis represents honour/status.

- Failure signs: Says Achilles is angry only because he loves Briseis romantically; misses honour/prize logic.

### Investigator response (v3 agentic)

```md
Question: Why does Achilles believe Agamemnon has dishonoured him?
Response: Achilles believes Agamemnon has dishonoured him because Agamemnon took away his prize, the daughter of Chryses, a priest of Apollo, without giving her back or accepting ransom for her [p.
Evidence:
- [p. 3 | p0003_full] Then 75 I will speak; yet make me a promise and swear before me readily by word and work of your hands to defend me, since I believe I shall make a man angry who holds great kingship over the men of Argos, and all the Achaians obey him. For a king when he is angry with a man beneath him is too strong, 80 and suppose even for the day itself he swallow down his anger, he still keeps bitterness that remains until its fulfilment deep in his chest. Speak forth then, tell me if you will protect me.' Then in answer again spoke Achilleus of the swift feet: 'Speak, interpreting whatever you know, and fear nothing. 85 In the name of Apollo beloved of Zeus to whom you, Kalchas, make your prayers when you interpret the gods' will to the Danaans, no man so long as I am alive above earth and see daylight shall lay the weight of his hands on you beside the hollow ships, not one of all the Danaans, even if you mean Agamemnon, 90 who now claims to be far the greatest of all the Achaians.' At this the b...
- [p. 10 | iliad_book1_p0010_c01] But now he has given me not even a little. Now the son of Atreus, powerful Agamemnon, 355 has dishonoured me, since he has taken away my prize and keeps it.' So he spoke in tears and the lady his mother heard him as she sat in the depths of the sea at the side of her aged father, and lightly she emerged like a mist from the grey water. 360 She came and sat beside him as he wept, and stroked him with her hand and called him by name and spoke to him: 'Why then, child, do you lament?
- [p. 1 | p0001_full] ONE BOOK S ING, goddess, the anger of Peleus' son Achilleus and its devastation, which put pains thousandfold upon the Achaians, hurled in their multitudes to the house of Hades strong souls of heroes, but gave their bodies to be the delicate feasting of dogs, of all birds, and the will of Zeus was accomplished 5 since that time when first there stood in division of conflict Atreus' son the lord of men and brilliant Achilleus. What god was it then set them together in bitter collision? Zeus' son and Leto's, Apollo, who in anger at the king drove the foul pestilence along the host, and the people perished, I0 since Atreus' son had dishonoured Chryses, priest of Apollo, when he came beside the fast ships of the Achaians to ransom back his daughter, carrying gifts beyond count and holding in his hands wound on a staff of gold the ribbons of Apollo who strikes from afar, and supplicated all the Achaians, 15 but above all Atreus' two sons, the marshals of the people: 'Sons of Atreus and you...
- [p. 5 | p0005_full] And now my prize you threaten in person to strip from me, for whom I laboured much, the gift of the sons of the Achaians. Never, when the Achaians sack some well-founded citadel of the Trojans, do I have a prize that is equal to your prize. 165 Always the greater part of the painful fighting is the work of my hands; but when the time comes to distribute the booty yours is far the greater reward, and I with some small thing yet dear to me go back to my ships when I am weary with fighting. Now I am returning to Phthia, since it is much better to go home again with my curved ships, and I am minded no longer 170 to stay here dishonoured and pile up your wealth and your luxury. Then answered him in turn the lord of men Agamemnon: 'Run away by all means if your heart drives you. I will not entreat you to stay here for my sake. There are others with me who will do me honour, and above all Zeus of the counsels.
- [p. 15 | p0015_full] or else refuse it, you have nothing to fear, that I may know 515 by how much I am the most dishonoured of all gods.' Deeply disturbed Zeus who gathers the clouds answered her: 'This is a disastrous matter when you set me in conflict with Hera, and she troubles me with recriminations. Since even as things are, forever among the immortals 520 she is at me and speaks of how I help the Trojans in battle. Even so, go back again now, go away, for fear she see us. I will look to these things that they be accomplished.
Diagnostics:
- retrieval_backend: vector
- vector_succeeded: True
- llm_succeeded: True
- pages_before_rerank: [3, 4, 7, 15, 1, 13, 5, 8, 14, 10]
- pages_after_expansion: [3, 3, 1, 5, 15, 15, 1, 5, 10, 4, 13, 8]
- followup_queries: ['Achilles dishonour Agamemnon reason', 'Agamemnon dishonours priest Chryses']
- pages_after_followup: [3, 3, 1, 5, 15, 1, 5, 10, 15, 4, 13, 8]
- evidence_sufficiency: {'sufficient': True, 'broad_question': False, 'cited_pages': [1, 3, 5, 10, 15], 'question_term_overlap': ['agamemnon', 'believe', 'dishonoured'], 'reason': 'ok'}
```

### Evaluation

**Verdict:** Mixed. v3 finally retrieves strong expected pages p. 5 and p. 10, but Qwen generates a wrong answer by blending Chryses/Chryseis with Achilles' prize. It says Agamemnon took “the daughter of Chryses” as Achilles' prize; the relevant prize is Briseis.

| Metric | Score | Notes |
|---|---:|---|
| retrieval_relevance | 4/5 | Includes p. 5 and p. 10, the key honour/prize pages, though p. 1/p. 3/p. 15 add noise. |
| citation_accuracy | 2/5 | Citations contain support, but generated claim misuses them. |
| speaker_attribution | 2/5 | Confuses whose daughter/prize is at issue. |
| causal_chain | 2/5 | Mentions prize removal but gets object wrong and misses fighting-for-Agamemnon logic. |
| no_hallucination | 1/5 | Serious Chryseis/Briseis-style hallucination. |
| answer_quality | 1/5 | Direct answer is misleading and malformed. |

**Delta vs v2:** Retrieval is much improved over v2's wrong Chryses-only trap, but generation is dangerous. This is exactly where stricter entity validation is needed.

## Q10. What is ironic about Achilles asking Zeus to help the Trojans?

**Test set:** D — Interpretive but source-grounded

### Expected

- Expected evidence: pp. 5, 12, 14–16

- Good answer should mention: Achilles is an Achaian warrior who fought against Troy, but because Agamemnon dishonoured him, he wants Trojan success so the Achaians suffer and recognize his value.

- Failure signs: Says Thetis asks Achilles to pray; says the irony is Zeus being suspicious; cites irrelevant p. 13.

### Investigator response (v3 agentic)

```md
Question: What is ironic about Achilles asking Zeus to help the Trojans?
Response: I could not produce a fully synthesized answer from the selected evidence. Best evidence:
- [p. 15] or else refuse it, you have nothing to fear, that I may know 515 by how much I am the most dishonoured of all gods.' Deeply disturbed Zeus who gathers the clouds answered her: 'This is a disastrous matter when you set me in conflict with He...
- [p. 8] He in kind intention toward both stood forth and addressed them: 'Oh, for shame. Great sorrow comes on the land of Achaia. Now might Priam and the sons of Priam in truth be happy, 255 and all the rest of the Trojans be visited in their hear...
- [p. 16] Now, though, I am terribly afraid you were won over SSS by Thetis the silver-footed, the daughter of the sea's ancient. For early in the morning she sat beside you and took your knees, and I think you bowed your head in assent to do honour...
Evidence:
- [p. 15 | p0015_full] or else refuse it, you have nothing to fear, that I may know 515 by how much I am the most dishonoured of all gods.' Deeply disturbed Zeus who gathers the clouds answered her: 'This is a disastrous matter when you set me in conflict with Hera, and she troubles me with recriminations. Since even as things are, forever among the immortals 520 she is at me and speaks of how I help the Trojans in battle. Even so, go back again now, go away, for fear she see us. I will look to these things that they be accomplished. See then, I will bend my head that you may believe me.
- [p. 8 | p0008_full] He in kind intention toward both stood forth and addressed them: 'Oh, for shame. Great sorrow comes on the land of Achaia. Now might Priam and the sons of Priam in truth be happy, 255 and all the rest of the Trojans be visited in their hearts with gladness, were they to hear all this wherein you two are quarrelling, you, who surpass all Danaans in council, in fighting. Yet be persuaded. Both of you are younger than I am. 260 Yes, and in my time I have dealt with better men than you are, and never once did they disregard me.
- [p. 16 | iliad_book1_p0016_c01] Now, though, I am terribly afraid you were won over SSS by Thetis the silver-footed, the daughter of the sea's ancient. For early in the morning she sat beside you and took your knees, and I think you bowed your head in assent to do honour to Achilleus, and to destroy many beside the ships of the Achaians.' Then in return Zeus who gathers the clouds made answer: 560 'Dear lady, I never escape you, you are always full of suspicion. Yet thus you can accomplish nothing surely, but be more distant from my heart than ever, and it will be the worse for you.
Diagnostics:
- retrieval_backend: vector
- vector_succeeded: True
- llm_succeeded: True
- pages_before_rerank: [3, 4, 15, 13, 7, 5, 14, 8, 16, 11]
- pages_after_expansion: [15, 15, 15, 4, 5, 14, 4, 5, 14, 8, 16, 4]
- followup_queries: ['Achilles asking Zeus to help Trojans irony', 'Zeus helping Trojans despite conflict with Hera']
- pages_after_followup: [15, 15, 15, 8, 8, 4, 5, 16, 4, 5, 14, 14]
- evidence_sufficiency: {'sufficient': True, 'broad_question': False, 'cited_pages': [8, 15, 16], 'question_term_overlap': ['help', 'trojans', 'zeus'], 'reason': 'ok'}
```

### Evaluation

**Verdict:** Retrieval improves versus v2 on consequences (p. 16) and Trojan benefit (p. 8/p. 15), but misses/underuses p. 12 and p. 5, and the response falls back to evidence. It no longer falsely says Thetis appeals on p. 8, but it does not answer the irony.

| Metric | Score | Notes |
|---|---:|---|
| retrieval_relevance | 3/5 | Includes p. 16 and p. 15; p. 8 is useful for Trojan joy at Achaian quarrel; missing p. 5/p. 12. |
| citation_accuracy | 4/5 | Evidence supports parts of the irony/consequence. |
| speaker_attribution | n/a | No synthesized claim. |
| causal_chain | 2/5 | Evidence shows pieces but not Achilles -> Thetis/Zeus -> Trojans -> Achaian suffering. |
| no_hallucination | 5/5 | Avoids v2 misattribution. |
| answer_quality | 1/5 | Does not answer. |

**Delta vs v2:** Safer and less hallucinatory, but still inadequate. Need role-aware follow-up queries that retrieve Achilles' own request on p. 12.

## Q11. How does Book 1 show that honour is both personal and political?

**Test set:** D — Interpretive but source-grounded

### Expected

- Expected evidence: pp. 1–16

- Good answer should mention: Personal insult to Chryses causes public plague; Agamemnon’s seizure of Briseis humiliates Achilles; Achilles’ anger harms the whole army; Thetis/Zeus turn the honour dispute into a war-level consequence.

- Failure signs: Only discusses Achilles’ emotions; ignores public/military consequences.

### Investigator response (v3 agentic)

```md
Question: How does Book 1 show that honour is both personal and political?
Response: I could not produce a fully synthesized answer from the selected evidence. Best evidence:
- [p. 3] Speak forth then, tell me if you will protect me.' Then in answer again spoke Achilleus of the swift feet: 'Speak, interpreting whatever you know, and fear nothing. 85 In the name of Apollo beloved of Zeus to whom you, Kalchas, make your pr...
- [p. 10] For surely in ruinous heart he makes sacrifice and has not wit enough to look behind and before him that the Achaians fighting beside their ships shall not perish.' So he spoke, and Patroklos obeyed his beloved companion. 345 He led forth f...
- [p. 8] And also these listened to the counsels I gave and heeded my bidding. Do you also obey, since to be persuaded is better. You, great man that you are, yet do not take the girl away 275 but let her be, a prize as the sons of the Achaians gave...
- [p. 9] Then they accomplished perfect hecatombs to Apollo, 315 of bulls and goats along the beach of the barren salt sea. The savour of the burning swept in circles up to the bright sky. Thus these were busy about the army. But Agamemnon did not g...
- [p. 11] We went against Thebe, the sacred city of Eëtion, and the city we sacked, and carried everything back to this place, and the sons of the Achaians made a fair distribution and for Atreus' son they chose out Chryseis of the fair cheeks. Then...
Evidence:
- [p. 3 | iliad_book1_p0003_c01] Speak forth then, tell me if you will protect me.' Then in answer again spoke Achilleus of the swift feet: 'Speak, interpreting whatever you know, and fear nothing. 85 In the name of Apollo beloved of Zeus to whom you, Kalchas, make your prayers when you interpret the gods' will to the Danaans, no man so long as I am alive above earth and see daylight shall lay the weight of his hands on you beside the hollow ships, not one of all the Danaans, even if you mean Agamemnon, 90 who now claims to be far the greatest of all the Achaians.' At this the blameless seer took courage again and spoke forth: 'No, it is not for the sake of some vow or hecatomb he blames us, but for the sake of his priest whom Agamemnon dishonoured and would not give him back his daughter nor accept the ransom. 95 Therefore the archer sent griefs against us and will send them still, nor sooner thrust back the shameful plague from the Danaans until we give the glancing-eyed girl back to her father without price, withou...
- [p. 10 | p0010_full] For surely in ruinous heart he makes sacrifice and has not wit enough to look behind and before him that the Achaians fighting beside their ships shall not perish.' So he spoke, and Patroklos obeyed his beloved companion. 345 He led forth from the hut Briseis of the fair cheeks and gave her to be taken away; and they walked back beside the ships of the Achaians, and the woman all unwilling went with them still. But Achilleus weeping went and sat in sorrow apart from his companions beside the beach of the grey sea looking out on the infinite water. 350 Many times stretching forth his hands he called on his mother: 'Since, my mother, you bore me to be a man with a short life, therefore Zeus of the loud thunder on Olympos should grant me honour at least. But now he has given me not even a little. Now the son of Atreus, powerful Agamemnon, 355 has dishonoured me, since he has taken away my prize and keeps it.' So he spoke in tears and the lady his mother heard him as she sat in the depths...
- [p. 8 | p0008_full] And also these listened to the counsels I gave and heeded my bidding. Do you also obey, since to be persuaded is better. You, great man that you are, yet do not take the girl away 275 but let her be, a prize as the sons of the Achaians gave her first. Nor, son of Peleus, think to match your strength with the king, since never equal with the rest is the portion of honour of the sceptred king to whom Zeus gives magnificence. Even 280 though you are the stronger man, and the mother who bore you was immortal, yet is this man greater who is lord over more than you rule: Son of Atreus, give up your anger; even I entreat you to give over your bitterness against Achilleus, he who stands as a great bulwark of battle over all the Achaians.' Then in answer again spoke powerful Agamemnon: 285 'Yes, old sir, all this you have said is fair and orderly. Yet here is a man who wishes to be above all others, who wishes to hold power over all, and to be lord of all, and give them their orders, yet I thin...
- [p. 9 | p0009_full] Then they accomplished perfect hecatombs to Apollo, 315 of bulls and goats along the beach of the barren salt sea. The savour of the burning swept in circles up to the bright sky. Thus these were busy about the army. But Agamemnon did not give up his anger and the first threat he made to Achilleus, but to Talthybios he gave his orders and Eurybates 320 who were heralds and hard-working henchmen to him: 'Go now to the shelter of Peleus' son Achilleus, to bring back Briseis of the fair cheeks leading her by the hand. And if he will not give her, I must come in person to take her with many men behind me, and it will be the worse for him.' 325 He spoke and sent them forth with this strong order upon them. They went against their will beside the beach of the barren [67]
- [p. 11 | p0011_full] We went against Thebe, the sacred city of Eëtion, and the city we sacked, and carried everything back to this place, and the sons of the Achaians made a fair distribution and for Atreus' son they chose out Chryseis of the fair cheeks. Then Chryses, priest of him who strikes from afar, Apollo, 370 came beside the fast ships of the bronze-armoured Achaians to ransom back his daughter, carrying gifts beyond count and holding in his hands wound on a staff of gold the ribbons of Apollo who strikes from afar, and supplicated all the Achaians, but above all Atreus' two sons, the marshals of the people. 375 Then all the rest of the Achaians cried out in favour that the priest be respected and the shining ransom be taken; yet this pleased not the heart of Atreus' son Agamemnon, but harshly he sent him away with a strong order upon him. The old man went back again in anger, but Apollo 380 listened to his prayer, since he was very dear to him, and let go the wicked arrow against the Argives. And...
Diagnostics:
- retrieval_backend: vector
- vector_succeeded: True
- llm_succeeded: True
- pages_before_rerank: [8, 7, 5, 1, 9, 6, 11, 14, 4, 3, 13, 16]
- pages_after_expansion: [9, 9, 10, 8, 9, 8, 11, 11, 8, 3, 3, 6]
- followup_queries: ['honour as personal and political in book 1 iliad', 'Achilleus honour actions showing personal and political']
- pages_after_followup: [10, 9, 9, 8, 10, 11, 8, 9, 11, 8, 11, 3]
- evidence_sufficiency: {'sufficient': False, 'broad_question': True, 'cited_pages': [3, 8, 9, 10, 11], 'question_term_overlap': ['honour'], 'reason': 'too few pages or too little question-term overlap'}
```

### Evaluation

**Verdict:** Retrieval is much stronger: final evidence covers Chryses/Kalchas/plague (p. 3/11), Briseis seizure (p. 9/10), and Nestor's political framing (p. 8). Sufficiency correctly flags too little question-term overlap, but response still falls back.

| Metric | Score | Notes |
|---|---:|---|
| retrieval_relevance | 4/5 | Broad useful coverage; still lacks p. 14-16 Zeus/Thetis consequence. |
| citation_accuracy | 4/5 | Evidence supports major personal-to-public links. |
| speaker_attribution | n/a | No synthesized answer. |
| causal_chain | 3/5 | Evidence supports chain better than prior versions. |
| no_hallucination | 5/5 | Safe fallback. |
| answer_quality | 1/5 | No interpretive synthesis. |

**Delta vs v2:** Big retrieval improvement. Remaining issue is strict generation/fallback and weak sufficiency semantics.

## Q12. How does Nestor try to resolve the conflict between Achilles and Agamemnon?

**Test set:** D — Interpretive but source-grounded

### Expected

- Expected evidence: p. 8

- Good answer should mention: Nestor urges restraint; acknowledges Achilles’ strength but Agamemnon’s greater authority; tries to preserve unity among the Achaians.

- Failure signs: Says Nestor takes Achilles’ side completely; says he orders Agamemnon to return Briseis.

### Investigator response (v3 agentic)

```md
Question: How does Nestor try to resolve the conflict between Achilles and Agamemnon?
Response: I could not produce a fully synthesized answer from the selected evidence. Best evidence:
- [p. 3] Then 75 I will speak; yet make me a promise and swear before me readily by word and work of your hands to defend me, since I believe I shall make a man angry who holds great kingship over the men of Argos, and all the Achaians obey him. For...
- [p. 7] And then you will eat out the heart within you in sorrow, that you did no honour to the best of the Achaians.' Thus spoke Peleus' son and dashed to the ground the sceptre 245 studded with golden nails, and sat down again. But Atreides raged...
- [p. 8] Nor, son of Peleus, think to match your strength with the king, since never equal with the rest is the portion of honour of the sceptred king to whom Zeus gives magnificence. Even 280 though you are the stronger man, and the mother who bore...
- [p. 9] Then they accomplished perfect hecatombs to Apollo, 315 of bulls and goats along the beach of the barren salt sea. The savour of the burning swept in circles up to the bright sky. Thus these were busy about the army. But Agamemnon did not g...
- [p. 11] We went against Thebe, the sacred city of Eëtion, and the city we sacked, and carried everything back to this place, and the sons of the Achaians made a fair distribution and for Atreus' son they chose out Chryseis of the fair cheeks. Then...
Evidence:
- [p. 3 | p0003_full] Then 75 I will speak; yet make me a promise and swear before me readily by word and work of your hands to defend me, since I believe I shall make a man angry who holds great kingship over the men of Argos, and all the Achaians obey him. For a king when he is angry with a man beneath him is too strong, 80 and suppose even for the day itself he swallow down his anger, he still keeps bitterness that remains until its fulfilment deep in his chest. Speak forth then, tell me if you will protect me.' Then in answer again spoke Achilleus of the swift feet: 'Speak, interpreting whatever you know, and fear nothing. 85 In the name of Apollo beloved of Zeus to whom you, Kalchas, make your prayers when you interpret the gods' will to the Danaans, no man so long as I am alive above earth and see daylight shall lay the weight of his hands on you beside the hollow ships, not one of all the Danaans, even if you mean Agamemnon, 90 who now claims to be far the greatest of all the Achaians.' At this the b...
- [p. 7 | iliad_book1_p0007_c01] And then you will eat out the heart within you in sorrow, that you did no honour to the best of the Achaians.' Thus spoke Peleus' son and dashed to the ground the sceptre 245 studded with golden nails, and sat down again. But Atreides raged still on the other side, and between them Nestor the fair-spoken rose up, the lucid speaker of Pylos, from whose lips the streams of words ran sweeter than honey. In his time two generations of mortal men had perished, 250 those who had grown up with him and they who had been born to these in sacred Pylos, and he was king in the third age.
- [p. 8 | iliad_book1_p0008_c01] Nor, son of Peleus, think to match your strength with the king, since never equal with the rest is the portion of honour of the sceptred king to whom Zeus gives magnificence. Even 280 though you are the stronger man, and the mother who bore you was immortal, yet is this man greater who is lord over more than you rule: Son of Atreus, give up your anger; even I entreat you to give over your bitterness against Achilleus, he who stands as a great bulwark of battle over all the Achaians.' Then in answer again spoke powerful Agamemnon: 285 'Yes, old sir, all this you have said is fair and orderly. Yet here is a man who wishes to be above all others, who wishes to hold power over all, and to be lord of all, and give them their orders, yet I think one will not obey him.
- [p. 9 | p0009_full] Then they accomplished perfect hecatombs to Apollo, 315 of bulls and goats along the beach of the barren salt sea. The savour of the burning swept in circles up to the bright sky. Thus these were busy about the army. But Agamemnon did not give up his anger and the first threat he made to Achilleus, but to Talthybios he gave his orders and Eurybates 320 who were heralds and hard-working henchmen to him: 'Go now to the shelter of Peleus' son Achilleus, to bring back Briseis of the fair cheeks leading her by the hand. And if he will not give her, I must come in person to take her with many men behind me, and it will be the worse for him.' 325 He spoke and sent them forth with this strong order upon them. They went against their will beside the beach of the barren [67]
- [p. 11 | p0011_full] We went against Thebe, the sacred city of Eëtion, and the city we sacked, and carried everything back to this place, and the sons of the Achaians made a fair distribution and for Atreus' son they chose out Chryseis of the fair cheeks. Then Chryses, priest of him who strikes from afar, Apollo, 370 came beside the fast ships of the bronze-armoured Achaians to ransom back his daughter, carrying gifts beyond count and holding in his hands wound on a staff of gold the ribbons of Apollo who strikes from afar, and supplicated all the Achaians, but above all Atreus' two sons, the marshals of the people. 375 Then all the rest of the Achaians cried out in favour that the priest be respected and the shining ransom be taken; yet this pleased not the heart of Atreus' son Agamemnon, but harshly he sent him away with a strong order upon him. The old man went back again in anger, but Apollo 380 listened to his prayer, since he was very dear to him, and let go the wicked arrow against the Argives. And...
Diagnostics:
- retrieval_backend: vector
- vector_succeeded: True
- llm_succeeded: True
- pages_before_rerank: [8, 7, 6, 3, 1, 16, 15, 4, 5, 9, 14, 11]
- pages_after_expansion: [9, 9, 11, 11, 3, 3, 6, 6, 10, 5, 8, 7]
- followup_queries: ['Nestor tries to mediate between Achilles and Agamemnon', 'Achilles and Agamemnon conflict resolution through Nestor']
- pages_after_followup: [9, 9, 11, 11, 3, 3, 6, 6, 10, 5, 8, 7]
- evidence_sufficiency: {'sufficient': True, 'broad_question': True, 'cited_pages': [3, 7, 8, 9, 11], 'question_term_overlap': ['agamemnon', 'between', 'nestor'], 'reason': 'ok'}
```

### Evaluation

**Verdict:** Expected p. 8 is present and relevant, but final output is evidence-only and polluted with unrelated pages. It contains Nestor telling Achilles not to match strength with the king and telling Agamemnon to give up anger, but misses in prose the full balanced mediation.

| Metric | Score | Notes |
|---|---:|---|
| retrieval_relevance | 3/5 | p. 8 present; p. 7 intro helps; p. 3/9/11 are distracting. |
| citation_accuracy | 3/5 | p. 8 supports expected answer; other citations do not. |
| speaker_attribution | n/a | No synthesized attribution. |
| causal_chain | 2/5 | Evidence implies mediation but not explained. |
| no_hallucination | 5/5 | Safe. |
| answer_quality | 1/5 | Fallback only. |

**Delta vs v2:** v2 had a partial direct answer; v3 has better/wider evidence but worse user-facing answer due to fallback.

## Q13. Find evidence that Agamemnon’s leadership damages the Achaian army.

**Test set:** E — Retrieval difficulty / abstract query

### Expected

- Expected evidence: pp. 1–5, 8–12

- Good answer should mention: His rejection of Chryses brings plague; his demand for compensation creates conflict with Achilles; taking Briseis leads Achilles to withdraw.

- Failure signs: Retrieves only p. 8 or only p. 1; does not connect multiple events.

### Investigator response (v3 agentic)

```md
Question: Find evidence that Agamemnon’s leadership damages the Achaian army.
Response: [66] [p.
Evidence:
- [p. 3 | p0003_full] Then 75 I will speak; yet make me a promise and swear before me readily by word and work of your hands to defend me, since I believe I shall make a man angry who holds great kingship over the men of Argos, and all the Achaians obey him. For a king when he is angry with a man beneath him is too strong, 80 and suppose even for the day itself he swallow down his anger, he still keeps bitterness that remains until its fulfilment deep in his chest. Speak forth then, tell me if you will protect me.' Then in answer again spoke Achilleus of the swift feet: 'Speak, interpreting whatever you know, and fear nothing. 85 In the name of Apollo beloved of Zeus to whom you, Kalchas, make your prayers when you interpret the gods' will to the Danaans, no man so long as I am alive above earth and see daylight shall lay the weight of his hands on you beside the hollow ships, not one of all the Danaans, even if you mean Agamemnon, 90 who now claims to be far the greatest of all the Achaians.' At this the b...
- [p. 8 | p0008_full] Do you also obey, since to be persuaded is better. You, great man that you are, yet do not take the girl away 275 but let her be, a prize as the sons of the Achaians gave her first. Nor, son of Peleus, think to match your strength with the king, since never equal with the rest is the portion of honour of the sceptred king to whom Zeus gives magnificence. Even 280 though you are the stronger man, and the mother who bore you was immortal, yet is this man greater who is lord over more than you rule: Son of Atreus, give up your anger; even I entreat you to give over your bitterness against Achilleus, he who stands as a great bulwark of battle over all the Achaians.' Then in answer again spoke powerful Agamemnon: 285 'Yes, old sir, all this you have said is fair and orderly. Yet here is a man who wishes to be above all others, who wishes to hold power over all, and to be lord of all, and give them their orders, yet I think one will not obey him. [66]
- [p. 9 | p0009_full] Then they accomplished perfect hecatombs to Apollo, 315 of bulls and goats along the beach of the barren salt sea. The savour of the burning swept in circles up to the bright sky. Thus these were busy about the army. But Agamemnon did not give up his anger and the first threat he made to Achilleus, but to Talthybios he gave his orders and Eurybates 320 who were heralds and hard-working henchmen to him: 'Go now to the shelter of Peleus' son Achilleus, to bring back Briseis of the fair cheeks leading her by the hand. And if he will not give her, I must come in person to take her with many men behind me, and it will be the worse for him.' 325 He spoke and sent them forth with this strong order upon them. They went against their will beside the beach of the barren [67]
- [p. 11 | p0011_full] We went against Thebe, the sacred city of Eëtion, and the city we sacked, and carried everything back to this place, and the sons of the Achaians made a fair distribution and for Atreus' son they chose out Chryseis of the fair cheeks. Then Chryses, priest of him who strikes from afar, Apollo, 370 came beside the fast ships of the bronze-armoured Achaians to ransom back his daughter, carrying gifts beyond count and holding in his hands wound on a staff of gold the ribbons of Apollo who strikes from afar, and supplicated all the Achaians, but above all Atreus' two sons, the marshals of the people. 375 Then all the rest of the Achaians cried out in favour that the priest be respected and the shining ransom be taken; yet this pleased not the heart of Atreus' son Agamemnon, but harshly he sent him away with a strong order upon him. The old man went back again in anger, but Apollo 380 listened to his prayer, since he was very dear to him, and let go the wicked arrow against the Argives. And...
- [p. 2 | iliad_book1_p0002_c01] 25 but harshly he drove him away with a strong order upon him: 'Never let me find you again, old sir, near our hollow ships, neither lingering now nor coming again hereafter, for fear your staff and the god's ribbons help you no longer. The girl I will not give back; sooner will old age come upon her 30 in my own house, in Argos, far from her own land, going up and down by the loom and being in my bed as my companion.
Diagnostics:
- retrieval_backend: vector
- vector_succeeded: True
- llm_succeeded: True
- pages_before_rerank: [9, 8, 1, 7, 11, 6, 5, 3, 4, 13, 2, 12]
- pages_after_expansion: [9, 9, 9, 11, 11, 8, 3, 8, 3, 8, 10, 2]
- followup_queries: ["Agamemnon's leadership conflicts with Achaian soldiers", "consequences of Agamemnon's authority on Achaians"]
- pages_after_followup: [9, 9, 9, 11, 11, 8, 3, 8, 3, 8, 10, 2]
- evidence_sufficiency: {'sufficient': True, 'broad_question': True, 'cited_pages': [2, 3, 8, 9, 11], 'question_term_overlap': ['agamemnon', 'army', 'find'], 'reason': 'ok'}
```

### Evaluation

**Verdict:** Retrieval is strong for multi-hop evidence: p. 2 Chryses rejection, p. 3 Kalchas/fear of king, p. 8 Nestor warning, p. 9 Briseis order, p. 11 recap. But answer is malformed (`[66] [p.`), a generation/validation failure.

| Metric | Score | Notes |
|---|---:|---|
| retrieval_relevance | 4/5 | Covers plague cause and Briseis/Achilles damage; could use p. 10/12 more. |
| citation_accuracy | 4/5 | Evidence supports expected points. |
| speaker_attribution | 1/5 | Generated response is malformed. |
| causal_chain | 3/5 | Evidence supports chain; no synthesized chain. |
| no_hallucination | 3/5 | No semantic hallucination, but malformed answer. |
| answer_quality | 0/5 | Unusable final response. |

**Delta vs v2:** Retrieval improved, generation regressed/failed. Next iteration should reject bracket-only/malformed answers and retry synthesis.

## Q14. Find evidence that divine power responds to human dishonour in Book 1.

**Test set:** E — Retrieval difficulty / abstract query

### Expected

- Expected evidence: pp. 1–3, 12, 14–16

- Good answer should mention: Apollo punishes Agamemnon’s dishonour of Chryses; Achilles/Thetis appeal to Zeus over Achilles’ dishonour.

- Failure signs: Mentions gods vaguely without explaining the human action that triggers divine response.

### Investigator response (v3 agentic)

```md
Question: Find evidence that divine power responds to human dishonour in Book 1.
Response: I could not produce a fully synthesized answer from the selected evidence. Best evidence:
- [p. 2] 25 but harshly he drove him away with a strong order upon him: 'Never let me find you again, old sir, near our hollow ships, neither lingering now nor coming again hereafter, for fear your staff and the god's ribbons help you no longer. The...
- [p. 8] You, great man that you are, yet do not take the girl away 275 but let her be, a prize as the sons of the Achaians gave her first. Nor, son of Peleus, think to match your strength with the king, since never equal with the rest is the portio...
- [p. 3] Speak forth then, tell me if you will protect me.' Then in answer again spoke Achilleus of the swift feet: 'Speak, interpreting whatever you know, and fear nothing. 85 In the name of Apollo beloved of Zeus to whom you, Kalchas, make your pr...
- [p. 11] 385 It was I first of all urged then the god's appeasement; and the anger took hold of Atreus' son, and in speed standing he uttered his threat against me, and now it is a thing accomplished. For the girl the glancing-eyed Achaians are taki...
- [p. 9] Then they accomplished perfect hecatombs to Apollo, 315 of bulls and goats along the beach of the barren salt sea. The savour of the burning swept in circles up to the bright sky. Thus these were busy about the army. But Agamemnon did not g...
Evidence:
- [p. 2 | p0002_full] 25 but harshly he drove him away with a strong order upon him: 'Never let me find you again, old sir, near our hollow ships, neither lingering now nor coming again hereafter, for fear your staff and the god's ribbons help you no longer. The girl I will not give back; sooner will old age come upon her 30 in my own house, in Argos, far from her own land, going up and down by the loom and being in my bed as my companion. So go now, do not make me angry; so you will be safer.' So he spoke, and the old man in terror obeyed him and went silently away beside the murmuring sea beach. 35 Over and over the old man prayed as he walked in solitude to King Apollo, whom Leto of the lovely hair bore: 'Hear me, lord of the silver bow who set your power about Chryse and Killa the sacrosanct, who are lord in strength over Tenedos, Smintheus, if ever it pleased your heart that I built your temple, 40 if ever it pleased you that I burned all the rich thigh pieces of bulls, of goats, then bring to pass thi...
- [p. 8 | p0008_full] You, great man that you are, yet do not take the girl away 275 but let her be, a prize as the sons of the Achaians gave her first. Nor, son of Peleus, think to match your strength with the king, since never equal with the rest is the portion of honour of the sceptred king to whom Zeus gives magnificence. Even 280 though you are the stronger man, and the mother who bore you was immortal, yet is this man greater who is lord over more than you rule: Son of Atreus, give up your anger; even I entreat you to give over your bitterness against Achilleus, he who stands as a great bulwark of battle over all the Achaians.' Then in answer again spoke powerful Agamemnon: 285 'Yes, old sir, all this you have said is fair and orderly. Yet here is a man who wishes to be above all others, who wishes to hold power over all, and to be lord of all, and give them their orders, yet I think one will not obey him. [66]
- [p. 3 | iliad_book1_p0003_c01] Speak forth then, tell me if you will protect me.' Then in answer again spoke Achilleus of the swift feet: 'Speak, interpreting whatever you know, and fear nothing. 85 In the name of Apollo beloved of Zeus to whom you, Kalchas, make your prayers when you interpret the gods' will to the Danaans, no man so long as I am alive above earth and see daylight shall lay the weight of his hands on you beside the hollow ships, not one of all the Danaans, even if you mean Agamemnon, 90 who now claims to be far the greatest of all the Achaians.' At this the blameless seer took courage again and spoke forth: 'No, it is not for the sake of some vow or hecatomb he blames us, but for the sake of his priest whom Agamemnon dishonoured and would not give him back his daughter nor accept the ransom. 95 Therefore the archer sent griefs against us and will send them still, nor sooner thrust back the shameful plague from the Danaans until we give the glancing-eyed girl back to her father without price, withou...
- [p. 11 | p0011_full] 385 It was I first of all urged then the god's appeasement; and the anger took hold of Atreus' son, and in speed standing he uttered his threat against me, and now it is a thing accomplished. For the girl the glancing-eyed Achaians are taking to Chryse in a fast ship, also carrying to the king presents. But even 390 now the heralds went away from my shelter leading Briseus' daughter, whom the sons of the Achaians gave me. You then, if you have power to, protect your own son, going to Olympos and supplicating Zeus, if ever before now either by word you comforted Zeus' heart or by action. 395 Since it is many times in my father's halls I have heard you making claims, when you said you only among the immortals beat aside shameful destruction from Kronos' son the dark-misted, that time when all the other Olympians sought to bind him, Hera and Poseidon and Pallas Athene. Then you, 400 goddess, went and set him free from his shackles, summoning in speed the creature of the hundred hands to t...
- [p. 9 | p0009_full] Then they accomplished perfect hecatombs to Apollo, 315 of bulls and goats along the beach of the barren salt sea. The savour of the burning swept in circles up to the bright sky. Thus these were busy about the army. But Agamemnon did not give up his anger and the first threat he made to Achilleus, but to Talthybios he gave his orders and Eurybates 320 who were heralds and hard-working henchmen to him: 'Go now to the shelter of Peleus' son Achilleus, to bring back Briseis of the fair cheeks leading her by the hand. And if he will not give her, I must come in person to take her with many men behind me, and it will be the worse for him.' 325 He spoke and sent them forth with this strong order upon them. They went against their will beside the beach of the barren [67]
Diagnostics:
- retrieval_backend: vector
- vector_succeeded: True
- llm_succeeded: True
- pages_before_rerank: [4, 1, 3, 13, 6, 11, 15, 8, 2, 7, 9, 16]
- pages_after_expansion: [11, 11, 9, 9, 2, 9, 2, 8, 8, 3, 8, 3]
- followup_queries: ['divine power response to human dishonour Book 1 Iliad', "Apollo responds to Agamemnon's prayer Book 1 Iliad"]
- pages_after_followup: [11, 11, 9, 9, 2, 9, 2, 8, 8, 3, 8, 10]
- evidence_sufficiency: {'sufficient': True, 'broad_question': True, 'cited_pages': [2, 3, 8, 9, 11], 'question_term_overlap': ['find', 'power'], 'reason': 'ok'}
```

### Evaluation

**Verdict:** Retrieval captures Apollo/Chryses chain well (p. 2, p. 3) and Achilles/Thetis appeal partly (p. 11), but misses p. 14-16 Zeus fulfillment. Final answer is fallback evidence.

| Metric | Score | Notes |
|---|---:|---|
| retrieval_relevance | 3/5 | Good Apollo evidence and some Achilles/Thetis request; missing Zeus assent/honour Achilles pages. |
| citation_accuracy | 4/5 | Cited evidence is relevant to human dishonour/divine response. |
| speaker_attribution | n/a | No synthesized answer. |
| causal_chain | 3/5 | Evidence supports first chain and start of second. |
| no_hallucination | 5/5 | Safe fallback. |
| answer_quality | 1/5 | No thematic synthesis. |

**Delta vs v2:** v3 better grounded than v2 and less misleading, but still incomplete.

## Q15. What role does Briseis play in the conflict, beyond being a captured woman?

**Test set:** E — Retrieval difficulty / abstract query

### Expected

- Expected evidence: pp. 6–10, 11–12

- Good answer should mention: Briseis functions as Achilles’ prize and symbol of honour; Agamemnon taking her publicly humiliates Achilles and triggers his withdrawal.

- Failure signs: Reduces Briseis only to romance; gives unsupported character analysis.

### Investigator response (v3 agentic)

```md
Question: What role does Briseis play in the conflict, beyond being a captured woman?
Response: I could not produce a fully synthesized answer from the selected evidence. Best evidence:
- [p. 10] For surely in ruinous heart he makes sacrifice and has not wit enough to look behind and before him that the Achaians fighting beside their ships shall not perish.' So he spoke, and Patroklos obeyed his beloved companion. 345 He led forth f...
- [p. 9] Then they accomplished perfect hecatombs to Apollo, 315 of bulls and goats along the beach of the barren salt sea. The savour of the burning swept in circles up to the bright sky. Thus these were busy about the army. But Agamemnon did not g...
- [p. 11] We went against Thebe, the sacred city of Eëtion, and the city we sacked, and carried everything back to this place, and the sons of the Achaians made a fair distribution and for Atreus' son they chose out Chryseis of the fair cheeks. Then...
- [p. 2] 25 but harshly he drove him away with a strong order upon him: 'Never let me find you again, old sir, near our hollow ships, neither lingering now nor coming again hereafter, for fear your staff and the god's ribbons help you no longer. The...
- [p. 3] Then 75 I will speak; yet make me a promise and swear before me readily by word and work of your hands to defend me, since I believe I shall make a man angry who holds great kingship over the men of Argos, and all the Achaians obey him. For...
Evidence:
- [p. 10 | p0010_adjacent] For surely in ruinous heart he makes sacrifice and has not wit enough to look behind and before him that the Achaians fighting beside their ships shall not perish.' So he spoke, and Patroklos obeyed his beloved companion. 345 He led forth from the hut Briseis of the fair cheeks and gave her to be taken away; and they walked back beside the ships of the Achaians, and the woman all unwilling went with them still. But Achilleus weeping went and sat in sorrow apart from his companions beside the beach of the grey sea looking out on the infinite water.
- [p. 9 | p0009_full] Then they accomplished perfect hecatombs to Apollo, 315 of bulls and goats along the beach of the barren salt sea. The savour of the burning swept in circles up to the bright sky. Thus these were busy about the army. But Agamemnon did not give up his anger and the first threat he made to Achilleus, but to Talthybios he gave his orders and Eurybates 320 who were heralds and hard-working henchmen to him: 'Go now to the shelter of Peleus' son Achilleus, to bring back Briseis of the fair cheeks leading her by the hand. And if he will not give her, I must come in person to take her with many men behind me, and it will be the worse for him.' 325 He spoke and sent them forth with this strong order upon them. They went against their will beside the beach of the barren [67]
- [p. 11 | p0011_full] We went against Thebe, the sacred city of Eëtion, and the city we sacked, and carried everything back to this place, and the sons of the Achaians made a fair distribution and for Atreus' son they chose out Chryseis of the fair cheeks. Then Chryses, priest of him who strikes from afar, Apollo, 370 came beside the fast ships of the bronze-armoured Achaians to ransom back his daughter, carrying gifts beyond count and holding in his hands wound on a staff of gold the ribbons of Apollo who strikes from afar, and supplicated all the Achaians, but above all Atreus' two sons, the marshals of the people. 375 Then all the rest of the Achaians cried out in favour that the priest be respected and the shining ransom be taken; yet this pleased not the heart of Atreus' son Agamemnon, but harshly he sent him away with a strong order upon him. The old man went back again in anger, but Apollo 380 listened to his prayer, since he was very dear to him, and let go the wicked arrow against the Argives. And...
- [p. 2 | p0002_full] 25 but harshly he drove him away with a strong order upon him: 'Never let me find you again, old sir, near our hollow ships, neither lingering now nor coming again hereafter, for fear your staff and the god's ribbons help you no longer. The girl I will not give back; sooner will old age come upon her 30 in my own house, in Argos, far from her own land, going up and down by the loom and being in my bed as my companion. So go now, do not make me angry; so you will be safer.' So he spoke, and the old man in terror obeyed him and went silently away beside the murmuring sea beach. 35 Over and over the old man prayed as he walked in solitude to King Apollo, whom Leto of the lovely hair bore: 'Hear me, lord of the silver bow who set your power about Chryse and Killa the sacrosanct, who are lord in strength over Tenedos, Smintheus, if ever it pleased your heart that I built your temple, 40 if ever it pleased you that I burned all the rich thigh pieces of bulls, of goats, then bring to pass thi...
- [p. 3 | p0003_full] Then 75 I will speak; yet make me a promise and swear before me readily by word and work of your hands to defend me, since I believe I shall make a man angry who holds great kingship over the men of Argos, and all the Achaians obey him. For a king when he is angry with a man beneath him is too strong, 80 and suppose even for the day itself he swallow down his anger, he still keeps bitterness that remains until its fulfilment deep in his chest. Speak forth then, tell me if you will protect me.' Then in answer again spoke Achilleus of the swift feet: 'Speak, interpreting whatever you know, and fear nothing. 85 In the name of Apollo beloved of Zeus to whom you, Kalchas, make your prayers when you interpret the gods' will to the Danaans, no man so long as I am alive above earth and see daylight shall lay the weight of his hands on you beside the hollow ships, not one of all the Danaans, even if you mean Agamemnon, 90 who now claims to be far the greatest of all the Achaians.' At this the b...
Diagnostics:
- retrieval_backend: vector
- vector_succeeded: True
- llm_succeeded: True
- pages_before_rerank: [4, 1, 13, 16, 9, 11, 15, 5, 3, 14, 6, 2]
- pages_after_expansion: [9, 9, 11, 11, 10, 12, 2, 2, 3, 3, 2, 3]
- followup_queries: ['Briseis conflict role', 'Achilleus Briseis relationship']
- pages_after_followup: [9, 9, 11, 11, 10, 12, 2, 2, 3, 3, 2, 3]
- evidence_sufficiency: {'sufficient': True, 'broad_question': True, 'cited_pages': [2, 3, 9, 10, 11], 'question_term_overlap': ['being', 'beyond', 'briseis', 'woman'], 'reason': 'ok'}
```

### Evaluation

**Verdict:** Retrieval is improved and directly relevant: p. 9 order to take Briseis, p. 10 removal and Achilles' sorrow, p. 11 broader prize/appeal context. However final answer is fallback and includes unrelated p. 2/p. 3 evidence.

| Metric | Score | Notes |
|---|---:|---|
| retrieval_relevance | 4/5 | Strong Briseis seizure/withdrawal evidence; missing p. 5/p. 6 explicit prize-honour logic. |
| citation_accuracy | 4/5 | Main p. 9/10/11 citations support role. |
| speaker_attribution | n/a | No synthesized claims. |
| causal_chain | 3/5 | Evidence shows seizure -> Achilles sorrow/withdrawal; symbolism needs synthesis. |
| no_hallucination | 5/5 | Safe fallback. |
| answer_quality | 1/5 | Does not answer interpretively. |

**Delta vs v2:** Retrieval better than v2, answer quality worse because v2 at least said “pawn”; v3 is safer but less useful.

## Q16. Write a 300-word answer: How does Book 1 present the relationship between anger, honour, and military disaster?

**Test set:** F — Essay-style RAG stress tests

### Expected

- Expected evidence: pp. 1–16

- Good answer should mention: Opening invocation, Apollo’s plague, Achilles/Agamemnon quarrel, Briseis, Thetis/Zeus.

- Failure signs: Over-focuses on one scene; weak citations; no chain of causality.

### Investigator response (v3 agentic)

```md
Question: Write a 300-word answer: How does Book 1 present the relationship between anger, honour, and military disaster?
Response: I could not produce a fully synthesized answer from the selected evidence. Best evidence:
- [p. 8] Nor, son of Peleus, think to match your strength with the king, since never equal with the rest is the portion of honour of the sceptred king to whom Zeus gives magnificence. Even 280 though you are the stronger man, and the mother who bore...
- [p. 6] So he spoke. And the anger came on Peleus' son, and within his shaggy breast the heart was divided two ways, pondering 190 whether to draw from beside his thigh the sharp sword, driving away all those who stood between and kill the son of A...
- [p. 9] Then they accomplished perfect hecatombs to Apollo, 315 of bulls and goats along the beach of the barren salt sea. The savour of the burning swept in circles up to the bright sky. Thus these were busy about the army. But Agamemnon did not g...
- [p. 7] Then in answer again spoke Achilleus of the swift feet: 215 'Goddess, it is necessary that I obey the word of you two, angry though I am in my heart. So it will be better. If any man obeys the gods, they listen to him also.' He spoke, and l...
- [p. 3] even an interpreter of dreams, since a dream also comes from Zeus, who can tell why Phoibos Apollo is so angry, if for the sake of some vow, some hecatomb he blames us, 65 if given the fragrant smoke of lambs, of he goats, somehow he can be...
Evidence:
- [p. 8 | iliad_book1_p0008_c01] Nor, son of Peleus, think to match your strength with the king, since never equal with the rest is the portion of honour of the sceptred king to whom Zeus gives magnificence. Even 280 though you are the stronger man, and the mother who bore you was immortal, yet is this man greater who is lord over more than you rule: Son of Atreus, give up your anger; even I entreat you to give over your bitterness against Achilleus, he who stands as a great bulwark of battle over all the Achaians.' Then in answer again spoke powerful Agamemnon: 285 'Yes, old sir, all this you have said is fair and orderly. Yet here is a man who wishes to be above all others, who wishes to hold power over all, and to be lord of all, and give them their orders, yet I think one will not obey him.
- [p. 6 | iliad_book1_p0006_c01] So he spoke. And the anger came on Peleus' son, and within his shaggy breast the heart was divided two ways, pondering 190 whether to draw from beside his thigh the sharp sword, driving away all those who stood between and kill the son of Atreus, or else to check the spleen within and keep down his anger. Now as he weighed in mind and spirit these two courses and was drawing from its scabbard the great sword, Athene descended 195 from the sky.
- [p. 9 | p0009_full] Then they accomplished perfect hecatombs to Apollo, 315 of bulls and goats along the beach of the barren salt sea. The savour of the burning swept in circles up to the bright sky. Thus these were busy about the army. But Agamemnon did not give up his anger and the first threat he made to Achilleus, but to Talthybios he gave his orders and Eurybates 320 who were heralds and hard-working henchmen to him: 'Go now to the shelter of Peleus' son Achilleus, to bring back Briseis of the fair cheeks leading her by the hand. And if he will not give her, I must come in person to take her with many men behind me, and it will be the worse for him.' 325 He spoke and sent them forth with this strong order upon them. They went against their will beside the beach of the barren [67]
- [p. 7 | p0007_full] Then in answer again spoke Achilleus of the swift feet: 215 'Goddess, it is necessary that I obey the word of you two, angry though I am in my heart. So it will be better. If any man obeys the gods, they listen to him also.' He spoke, and laid his heavy hand on the silver sword hilt and thrust the great blade back into the scabbard nor disobeyed 220 the word of Athene. And she went back again to Olympos to the house of Zeus of the aegis with the other divinities.
- [p. 3 | p0003_full] even an interpreter of dreams, since a dream also comes from Zeus, who can tell why Phoibos Apollo is so angry, if for the sake of some vow, some hecatomb he blames us, 65 if given the fragrant smoke of lambs, of he goats, somehow he can be made willing to beat the bane aside from us.' He spoke thus and sat down again, and among them stood up Kalchas, Thestor's son, far the best of the bird interpreters, who knew all things that were, the things to come and the things past, 70 who guided into the land of Ilion the ships of the Achaians through that seercraft of his own that Phoibos Apollo gave him. He in kind intention toward all stood forth and addressed them: 'You have bidden me, Achilleus beloved of Zeus, to explain to you this anger of Apollo the lord who strikes from afar. Then 75 I will speak; yet make me a promise and swear before me readily by word and work of your hands to defend me, since I believe I shall make a man angry who holds great kingship over the men of Argos, and a...
Diagnostics:
- retrieval_backend: vector
- vector_succeeded: True
- llm_succeeded: True
- pages_before_rerank: [7, 9, 6, 16, 2, 5, 8, 4, 11, 3, 15, 14]
- pages_after_expansion: [9, 9, 3, 7, 11, 3, 7, 11, 14, 8, 6, 8]
- followup_queries: ['anger and honor in iliad book 1 military disaster', 'relationship between anger honour and military failure in iliad book 1']
- pages_after_followup: [9, 9, 3, 3, 7, 7, 11, 11, 14, 8, 6, 10]
- evidence_sufficiency: {'sufficient': True, 'broad_question': True, 'cited_pages': [3, 6, 7, 8, 9], 'question_term_overlap': ['anger', 'answer', 'between', 'honour', 'word'], 'reason': 'ok'}
```

### Evaluation

**Verdict:** Retrieval covers several useful theme nodes: p. 3 Apollo anger/Kalchas, p. 6 Achilles' near-violence, p. 7 Athena restraint, p. 8 honour hierarchy/Nestor, p. 9 Briseis seizure. It still misses opening p. 1 and Thetis/Zeus endgame. Final response is not an essay.

| Metric | Score | Notes |
|---|---:|---|
| retrieval_relevance | 3/5 | Better middle-conflict coverage; incomplete book-wide arc. |
| citation_accuracy | 4/5 | Evidence is relevant. |
| speaker_attribution | n/a | No essay. |
| causal_chain | 2/5 | Evidence fragments, no synthesized chain. |
| no_hallucination | 5/5 | Safe fallback. |
| answer_quality | 0/5 | Ignores 300-word requirement. |

**Delta vs v2:** Retrieval broader in the quarrel section, but same essay-generation failure.

## Q17. Write a 500-word answer: In Book 1, how do priests, prophets, warriors, kings, and gods each shape the conflict?

**Test set:** F — Essay-style RAG stress tests

### Expected

- Expected evidence: pp. 1–16

- Good answer should mention: Chryses, Kalchas, Achilles, Agamemnon, Thetis, Zeus, Hera.

- Failure signs: Omits Chryses/Kalchas; confuses speakers; cites loosely.

### Investigator response (v3 agentic)

```md
Question: Write a 500-word answer: In Book 1, how do priests, prophets, warriors, kings, and gods each shape the conflict?
Response: I could not produce a fully synthesized answer from the selected evidence. Best evidence:
- [p. 1] ONE BOOK S ING, goddess, the anger of Peleus' son Achilleus and its devastation, which put pains thousandfold upon the Achaians, hurled in their multitudes to the house of Hades strong souls of heroes, but gave their bodies to be the delica...
- [p. 8] Nor, son of Peleus, think to match your strength with the king, since never equal with the rest is the portion of honour of the sceptred king to whom Zeus gives magnificence. Even 280 though you are the stronger man, and the mother who bore...
- [p. 7] Then in answer again spoke Achilleus of the swift feet: 215 'Goddess, it is necessary that I obey the word of you two, angry though I am in my heart. So it will be better. If any man obeys the gods, they listen to him also.' He spoke, and l...
- [p. 3] Then 75 I will speak; yet make me a promise and swear before me readily by word and work of your hands to defend me, since I believe I shall make a man angry who holds great kingship over the men of Argos, and all the Achaians obey him. For...
- [p. 9] And if the everlasting gods have made him a spearman, 290 yet they have not given him the right to speak abusively.' Then looking at him darkly brilliant Achilleus answered him: 'So must I be called of no account and a coward if I must carr...
Evidence:
- [p. 1 | iliad_book1_p0001_c01] ONE BOOK S ING, goddess, the anger of Peleus' son Achilleus and its devastation, which put pains thousandfold upon the Achaians, hurled in their multitudes to the house of Hades strong souls of heroes, but gave their bodies to be the delicate feasting of dogs, of all birds, and the will of Zeus was accomplished 5 since that time when first there stood in division of conflict Atreus' son the lord of men and brilliant Achilleus. What god was it then set them together in bitter collision?
- [p. 8 | iliad_book1_p0008_c01] Nor, son of Peleus, think to match your strength with the king, since never equal with the rest is the portion of honour of the sceptred king to whom Zeus gives magnificence. Even 280 though you are the stronger man, and the mother who bore you was immortal, yet is this man greater who is lord over more than you rule: Son of Atreus, give up your anger; even I entreat you to give over your bitterness against Achilleus, he who stands as a great bulwark of battle over all the Achaians.' Then in answer again spoke powerful Agamemnon: 285 'Yes, old sir, all this you have said is fair and orderly. Yet here is a man who wishes to be above all others, who wishes to hold power over all, and to be lord of all, and give them their orders, yet I think one will not obey him.
- [p. 7 | p0007_full] Then in answer again spoke Achilleus of the swift feet: 215 'Goddess, it is necessary that I obey the word of you two, angry though I am in my heart. So it will be better. If any man obeys the gods, they listen to him also.' He spoke, and laid his heavy hand on the silver sword hilt and thrust the great blade back into the scabbard nor disobeyed 220 the word of Athene. And she went back again to Olympos to the house of Zeus of the aegis with the other divinities. But Peleus' son once again in words of derision spoke to Atreides, and did not yet let go of his anger: 'You wine sack, with a dog's eyes, with a deer's heart. Never 225 once have you taken courage in your heart to arm with your people for battle, or go into ambuscade with the best of the Achaians.
- [p. 3 | p0003_full] Then 75 I will speak; yet make me a promise and swear before me readily by word and work of your hands to defend me, since I believe I shall make a man angry who holds great kingship over the men of Argos, and all the Achaians obey him. For a king when he is angry with a man beneath him is too strong, 80 and suppose even for the day itself he swallow down his anger, he still keeps bitterness that remains until its fulfilment deep in his chest. Speak forth then, tell me if you will protect me.' Then in answer again spoke Achilleus of the swift feet: 'Speak, interpreting whatever you know, and fear nothing. 85 In the name of Apollo beloved of Zeus to whom you, Kalchas, make your prayers when you interpret the gods' will to the Danaans, no man so long as I am alive above earth and see daylight shall lay the weight of his hands on you beside the hollow ships, not one of all the Danaans, even if you mean Agamemnon, 90 who now claims to be far the greatest of all the Achaians.' At this the b...
- [p. 9 | p0009_full] And if the everlasting gods have made him a spearman, 290 yet they have not given him the right to speak abusively.' Then looking at him darkly brilliant Achilleus answered him: 'So must I be called of no account and a coward if I must carry out every order you may happen to give me. Tell other men to do these things, but give me no more 295 commands, since I for my part have no intention to obey you. And put away in your thoughts this other thing I tell you. With my hands I will not fight for the girl's sake, neither with you nor any other man, since you take her away who gave her.
Diagnostics:
- retrieval_backend: vector
- vector_succeeded: True
- llm_succeeded: True
- pages_before_rerank: [7, 8, 9, 13, 6, 15, 11, 2, 3, 16, 4, 1]
- pages_after_expansion: [11, 11, 9, 9, 3, 3, 10, 7, 7, 1, 8, 6]
- followup_queries: ['priests and conflict shaping in iliad book 1', 'prophets role in iliad book 1 conflict']
- pages_after_followup: [11, 11, 9, 9, 3, 3, 10, 7, 7, 1, 8, 8]
- evidence_sufficiency: {'sufficient': True, 'broad_question': True, 'cited_pages': [1, 3, 7, 8, 9], 'question_term_overlap': ['answer', 'book', 'conflict', 'gods', 'word'], 'reason': 'ok'}
```

### Evaluation

**Verdict:** Retrieval has useful anchors for opening conflict (p. 1), prophet/king fear (p. 3), warrior/god interaction (p. 7), kingly authority (p. 8), and obedience conflict (p. 9). It still misses Thetis/Zeus/Hera endgame and Chryses detail. Final response is fallback evidence, not essay.

| Metric | Score | Notes |
|---|---:|---|
| retrieval_relevance | 3/5 | Several required categories represented, but gods/Thetis/Zeus/Hera weak. |
| citation_accuracy | 4/5 | Evidence supports partial role analysis. |
| speaker_attribution | n/a | No synthesized essay. |
| causal_chain | 2/5 | Some chain pieces; no full role synthesis. |
| no_hallucination | 5/5 | Safe fallback. |
| answer_quality | 0/5 | Not 500 words and omits required figures in answer. |

**Delta vs v2:** Similar failure; v3 evidence mix is somewhat better for roles but still no synthesis.

## Q18. Write a 500-word answer: Is Agamemnon’s authority portrayed as legitimate, abusive, or both in Book 1?

**Test set:** F — Essay-style RAG stress tests

### Expected

- Expected evidence: pp. 1–10

- Good answer should mention: He is king/commander, but rejects Chryses harshly, attacks Kalchas, demands compensation, and takes Briseis.

- Failure signs: Gives a one-sided answer with no evidence for rank/authority.

### Investigator response (v3 agentic)

```md
Question: Write a 500-word answer: Is Agamemnon’s authority portrayed as legitimate, abusive, or both in Book 1?
Response: I could not produce a fully synthesized answer from the selected evidence. Best evidence:
- [p. 8] Do you also obey, since to be persuaded is better. You, great man that you are, yet do not take the girl away 275 but let her be, a prize as the sons of the Achaians gave her first. Nor, son of Peleus, think to match your strength with the...
- [p. 3] Then 75 I will speak; yet make me a promise and swear before me readily by word and work of your hands to defend me, since I believe I shall make a man angry who holds great kingship over the men of Argos, and all the Achaians obey him. For...
- [p. 6] Yet will I tell you this thing, and I think it shall be accomplished. By such acts of arrogance he may even lose his own life.' 205 Then in answer the goddess grey-eyed Athene spoke to him: 'I have come down to stay your anger—but will you...
- [p. 9] Then they accomplished perfect hecatombs to Apollo, 315 of bulls and goats along the beach of the barren salt sea. The savour of the burning swept in circles up to the bright sky. Thus these were busy about the army. But Agamemnon did not g...
- [p. 11] We went against Thebe, the sacred city of Eëtion, and the city we sacked, and carried everything back to this place, and the sons of the Achaians made a fair distribution and for Atreus' son they chose out Chryseis of the fair cheeks. Then...
Evidence:
- [p. 8 | p0008_full] Do you also obey, since to be persuaded is better. You, great man that you are, yet do not take the girl away 275 but let her be, a prize as the sons of the Achaians gave her first. Nor, son of Peleus, think to match your strength with the king, since never equal with the rest is the portion of honour of the sceptred king to whom Zeus gives magnificence. Even 280 though you are the stronger man, and the mother who bore you was immortal, yet is this man greater who is lord over more than you rule: Son of Atreus, give up your anger; even I entreat you to give over your bitterness against Achilleus, he who stands as a great bulwark of battle over all the Achaians.' Then in answer again spoke powerful Agamemnon: 285 'Yes, old sir, all this you have said is fair and orderly. Yet here is a man who wishes to be above all others, who wishes to hold power over all, and to be lord of all, and give them their orders, yet I think one will not obey him. [66]
- [p. 3 | p0003_full] Then 75 I will speak; yet make me a promise and swear before me readily by word and work of your hands to defend me, since I believe I shall make a man angry who holds great kingship over the men of Argos, and all the Achaians obey him. For a king when he is angry with a man beneath him is too strong, 80 and suppose even for the day itself he swallow down his anger, he still keeps bitterness that remains until its fulfilment deep in his chest. Speak forth then, tell me if you will protect me.' Then in answer again spoke Achilleus of the swift feet: 'Speak, interpreting whatever you know, and fear nothing. 85 In the name of Apollo beloved of Zeus to whom you, Kalchas, make your prayers when you interpret the gods' will to the Danaans, no man so long as I am alive above earth and see daylight shall lay the weight of his hands on you beside the hollow ships, not one of all the Danaans, even if you mean Agamemnon, 90 who now claims to be far the greatest of all the Achaians.' At this the b...
- [p. 6 | iliad_book1_p0006_c01] Yet will I tell you this thing, and I think it shall be accomplished. By such acts of arrogance he may even lose his own life.' 205 Then in answer the goddess grey-eyed Athene spoke to him: 'I have come down to stay your anger—but will you obey me?— from the sky; and the goddess of the white arms Hera sent me, who loves both of you equally in her heart and cares for you. Come then, do not take your sword in your hand, keep clear of fighting, 210 though indeed with words you may abuse him, and it will be that way.
- [p. 9 | p0009_full] Then they accomplished perfect hecatombs to Apollo, 315 of bulls and goats along the beach of the barren salt sea. The savour of the burning swept in circles up to the bright sky. Thus these were busy about the army. But Agamemnon did not give up his anger and the first threat he made to Achilleus, but to Talthybios he gave his orders and Eurybates 320 who were heralds and hard-working henchmen to him: 'Go now to the shelter of Peleus' son Achilleus, to bring back Briseis of the fair cheeks leading her by the hand. And if he will not give her, I must come in person to take her with many men behind me, and it will be the worse for him.' 325 He spoke and sent them forth with this strong order upon them. They went against their will beside the beach of the barren [67]
- [p. 11 | p0011_full] We went against Thebe, the sacred city of Eëtion, and the city we sacked, and carried everything back to this place, and the sons of the Achaians made a fair distribution and for Atreus' son they chose out Chryseis of the fair cheeks. Then Chryses, priest of him who strikes from afar, Apollo, 370 came beside the fast ships of the bronze-armoured Achaians to ransom back his daughter, carrying gifts beyond count and holding in his hands wound on a staff of gold the ribbons of Apollo who strikes from afar, and supplicated all the Achaians, but above all Atreus' two sons, the marshals of the people. 375 Then all the rest of the Achaians cried out in favour that the priest be respected and the shining ransom be taken; yet this pleased not the heart of Atreus' son Agamemnon, but harshly he sent him away with a strong order upon him. The old man went back again in anger, but Apollo 380 listened to his prayer, since he was very dear to him, and let go the wicked arrow against the Argives. And...
Diagnostics:
- retrieval_backend: vector
- vector_succeeded: True
- llm_succeeded: True
- pages_before_rerank: [7, 9, 4, 6, 3, 15, 16, 8, 11, 1, 13, 14]
- pages_after_expansion: [8, 8, 3, 3, 11, 11, 9, 9, 8, 10, 9, 6]
- followup_queries: None
- pages_after_followup: None
- evidence_sufficiency: {'sufficient': True, 'broad_question': True, 'cited_pages': [3, 6, 8, 9, 11], 'question_term_overlap': ['agamemnon', 'answer', 'both', 'word'], 'reason': 'ok'}
```

### Evaluation

**Verdict:** Retrieval improves balance: p. 3 and p. 8 show legitimate/ranked authority; p. 9 and p. 11 show abusive seizure/rejection; p. 6 includes Achilles/Athena around arrogance but not the best p. 4/p. 6 threat. Final answer is fallback, not essay.

| Metric | Score | Notes |
|---|---:|---|
| retrieval_relevance | 4/5 | Good legitimate and abusive evidence; missing p. 2/p. 4 direct abuse in final set. |
| citation_accuracy | 4/5 | Evidence supports a both-sided answer. |
| speaker_attribution | n/a | No synthesized thesis. |
| causal_chain | 3/5 | Evidence supports authority -> abuse -> Briseis consequences. |
| no_hallucination | 5/5 | Safe fallback. |
| answer_quality | 0/5 | Does not answer essay prompt. |

**Delta vs v2:** Retrieval modestly better; generation unchanged/fallback. Next iteration needs an essay-mode synthesis prompt and retry when answer is fallback.
