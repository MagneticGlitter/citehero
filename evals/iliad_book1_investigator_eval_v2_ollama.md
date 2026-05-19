# Iliad Book 1 Investigator/RAG Drill-Down Evaluation v2 — Ollama/Qwen Enabled

This v2 artifact reruns the same 18 investigator prompts after starting local Ollama and verifying `qwen2.5-deterministic` is available. It uses the same markdown-only drill-down process as v1: no deterministic unit-test files. Each response was generated with `python main.py ask --reading-id iliad_book1 --top-k 10 --answer-model qwen2.5-deterministic`, then evaluated by a separate subagent.

## Environment check

- Ollama server was started locally on `http://localhost:11434`.
- Available models included `nomic-embed-text:latest`, `qwen2.5:latest`, and `qwen2.5-deterministic:latest`.
- This means v2 tests answer generation with Qwen instead of relying only on fallback evidence snippets.

## Cross-case summary

- Qwen improves some simple/direct cases by producing prose instead of only `Best evidence`, especially Q3 and Q12.
- However, it also introduces several worse failures: wrong speaker/action attribution, Chryseis/Briseis confusion, malformed/truncated answers, and unsupported claims from weak evidence.
- Retrieval/reranking remains the primary bottleneck for many questions: expected pages are often absent or the right page is retrieved but the selected span stops before the decisive lines.
- For essay/multi-hop questions, v2 still often falls back to evidence-list style or retrieves only 1–3 narrow pages instead of broad coverage.
- Net insight: enabling Qwen alone does not fix the investigator. It makes generation more fluent in some cases, but without evidence sufficiency checks and iterative retrieval, fluency can amplify bad retrieval into misleading answers.

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

### Investigator response \(v2 Ollama/Qwen\)

```md
Question: Who is Chryses, and what does he ask the Achaians to do?
Response: He states, "Come, now, we must haul a black ship down to the bright sea, and assemble rowers enough for it, and put on board it the hecatomb, and the girl herself, Chryseis of the fair cheeks..." (p.
Evidence:
- [p. 8 | iliad_book1_p0008_c01] Even 280 though you are the stronger man, and the mother who bore you was immortal, yet is this man greater who is lord over more than you rule: Son of Atreus, give up your anger; even I entreat you to give over your bitterness against Achilleus, he who stands as a great bulwark of battle over all the Achaians.' Then in answer again spoke powerful Agamemnon: 285 'Yes, old sir, all this you have said is fair and orderly.
- [p. 5 | iliad_book1_p0005_c01] I40 Come, now, we must haul a black ship down to the bright sea, and assemble rowers enough for it, and put on board it the hecatomb, and the girl herself, Chryseis of the fair cheeks, and let there be one responsible man in charge of her, either Aias or Idomeneus or brilliant Odysseus, 145 or you yourself, son of Peleus, most terrifying of all men, to reconcile by accomplishing sacrifice the archer.' Then looking darkly at him Achilleus of the swift feet spoke: 'O wrapped in shamelessness, with...
- [p. 4 | iliad_book1_p0004_c01] No, for the present give the girl back to the god; we Achaians thrice and four times over will repay you, if ever Zeus gives into our hands the strong-walled citadel of Troy to be plundered.' I30 Then in answer again spoke powerful Agamemnon: 'Not that way, good fighter though you be, godlike Achilleus, strive to cheat, for you will not deceive, you will not persuade me.
```

### Subagent evaluation

**Question:** Who is Chryses, and what does he ask the Achaians to do?  
**Expected pages:** pp. 1–2  
**Expected answer:** Chryses is a priest of Apollo. He comes to the Achaian ships with ransom, asking the Achaians/Atreids to return his daughter Chryseis and accept the ransom. Agamemnon rejects him harshly.

## v2 response assessed

The response says only:

> He states, "Come, now, we must haul a black ship down to the bright sea..." (p.

It then cites p. 8, p. 5, and p. 4.

## Lightweight checks

- **Expected-page coverage:** Fail. It retrieves/cites neither p. 1 nor p. 2, the primary expected evidence.  
- **Core facts present:** Fail/very weak. It does not say Chryses is Apollo's priest, does not say he brought ransom, and does not clearly say he asks for his daughter back.  
- **Agamemnon rejection:** Mostly missing. p. 4/p. 5 occur after the initial rejection and concern the later assembly discussion about returning Chryseis, not Chryses' original supplication.  
- **Forbidden failure signs:** Partial fail. It does not explicitly call Chryses a warrior or confuse him by name with Chryseis, but it effectively answers with Agamemnon's later plan about Chryseis rather than Chryses' request.  
- **Citation support:** Poor. The cited p. 5 quote is Agamemnon discussing how to send Chryseis back, not Chryses asking the Achaians anything. p. 8 is irrelevant to Q1.

## Rubric scores

| Criterion | Score | Notes |
|---|---:|---|
| retrieval_relevance | 1/5 | Misses expected pp. 1–2. p. 4/p. 5 are tangential later consequences; p. 8 is irrelevant. |
| citation_accuracy | 1/5 | The main quoted answer is not Chryses' speech/request and does not support who Chryses is. |
| speaker_attribution | 0/5 | Says/strongly implies Chryses “states” a passage actually spoken by Agamemnon in the later assembly. |
| causal_chain | 1/5 | Does not preserve the sequence: Chryses supplicates → Agamemnon rejects → Apollo plague. |
| no_hallucination | 2/5 | Mostly copied from source, but the attribution/use of the quote is unsupported and misleading. |
| answer_quality | 0/5 | Incomplete, truncated, and does not answer either part of the question directly. |

## Diagnosis

- **Primary failure: retrieval/reranking.** The system did not surface the key early pages. It over-selected later passages about returning Chryseis and Achaian quarrel logistics, apparently matching terms like “Chryseis,” “girl,” and “give back,” while missing the actual Chryses passage on pp. 1–2.
- **Secondary failure: generation.** The generator did not recognize that the retrieved quote was from Agamemnon, not Chryses, and produced a truncated, misleading answer.
- **OCR:** Not the issue. Pages 1–2 are readable and contain the needed answer clearly.
- **Prompt/format:** The response is not just evidence-dump style; it attempts an answer but chooses the wrong speaker/event and fails to synthesize the requested facts.

## Delta vs v1 / Qwen judgment

Compared with the v1 Q1 evaluation, **v2 is worse**. v1 at least retrieved p. 1 and p. 11, which identify Chryses as Apollo's priest and his ransom request, though it failed to synthesize a direct answer. v2 loses that relevant evidence and gives a misleading, wrongly attributed later quote. Qwen/Ollama did **not** improve Q1; the failure shifted from mainly generation/formatting in v1 to combined retrieval/reranking plus generation error in v2.

## Overall judgment

**Unsatisfactory.** For this simple factual lookup, v2 misses the expected source pages and does not answer the question. A correct answer would be: Chryses is Apollo's priest; he asks the Achaians, especially Agamemnon and Menelaos, to accept ransom and return his daughter Chryseis; Agamemnon refuses and drives him away.

## Q2. Who is Kalchas, and why is he afraid to speak?

**Test set:** A — Simple factual lookup

### Expected

- Expected evidence: p. 3

- Good answer should mention: Kalchas is a seer/bird-interpreter; he knows the cause of Apollo’s anger; he fears Agamemnon’s reaction; Achilles promises protection.

- Failure signs: Says Kalchas was dishonoured by Agamemnon; confuses him with Chryses.

### Investigator response \(v2 Ollama/Qwen\)

```md
Question: Who is Kalchas, and why is he afraid to speak?
Response: Kalchas is a seer who interprets the gods' will for the Danaans.
Evidence:
- [p. 3 | iliad_book1_p0003_c01] 85 In the name of Apollo beloved of Zeus to whom you, Kalchas, make your prayers when you interpret the gods' will to the Danaans, no man so long as I am alive above earth and see daylight shall lay the weight of his hands on you beside the hollow ships, not one of all the Danaans, even if you mean Agamemnon, 90 who now claims to be far the greatest of all the Achaians.' At this the blameless seer took courage again and spoke forth: 'No, it is not for the sake of some vow or hecatomb he blames u...
- [p. 9 | iliad_book1_p0009_c01] But Agamemnon did not give up his anger and the first threat he made to Achilleus, but to Talthybios he gave his orders and Eurybates 320 who were heralds and hard-working henchmen to him: 'Go now to the shelter of Peleus' son Achilleus, to bring back Briseis of the fair cheeks leading her by the hand.
```

### Subagent evaluation

**Question:** Who is Kalchas, and why is he afraid to speak?  
**Expected evidence:** p. 3  
**Expected answer elements:** Kalchas is a seer / bird-interpreter; he knows the cause of Apollo’s anger; he fears Agamemnon’s reaction; Achilles promises protection.

## V2 response assessed

> Kalchas is a seer who interprets the gods' will for the Danaans.

Evidence cited:
- p. 3: Achilles promises Kalchas protection, including from Agamemnon; Kalchas then begins explaining Apollo’s anger.
- p. 9: Agamemnon sends heralds to take Briseis from Achilles — not relevant to identifying Kalchas or his fear in this scene.

## Lightweight checks

- **Expected-page coverage:** Partial/pass. The response retrieves **p. 3**, the key page, but the shown chunk starts at Achilles’ reassurance and misses the earlier lines identifying Kalchas as “Thestor’s son” and “far the best of the bird interpreters,” as well as Kalchas’s own statement that he fears angering a powerful king.
- **Answer completeness:** Partial fail. The response directly identifies Kalchas as a seer, but does **not answer why he is afraid to speak**.
- **Citation support:** Partial. The p. 3 evidence supports Achilles’ protection and implies Agamemnon is the feared man, but because the answer omits that part, citation use is incomplete. The p. 9 citation is irrelevant.
- **Forbidden failure signs:** Pass. It does not say Kalchas was dishonoured by Agamemnon and does not confuse him with Chryses.
- **OCR check:** OCR is not the blocker. Page 3 is readable and contains all needed facts.

## Rubric scores

| Criterion | Score | Notes |
|---|---:|---|
| retrieval_relevance | 3/5 | Correctly retrieves p. 3, but snippet selection is too narrow and an irrelevant p. 9 result is included. |
| citation_accuracy | 3/5 | p. 3 supports part of the answer; p. 9 does not support this question. |
| speaker_attribution | 3/5 | No clear misattribution, but the response does not explain that Kalchas asks Achilles for protection and Achilles replies. |
| causal_chain | 2/5 | The causal reason for fear is missing: Kalchas will reveal that Agamemnon caused Apollo’s anger and fears Agamemnon’s retaliation. |
| no_hallucination | 5/5 | The stated claim is supported and no invented claim appears. |
| answer_quality | 2/5 | Better than an evidence dump because it gives one direct sentence, but it answers only “who” and misses “why afraid.” |

## Diagnosis

- **Primary failure: generation.** The model had enough p. 3 evidence to infer the answer but generated only a partial response.
- **Secondary failure: retrieval/reranking/snippet selection.** Retrieval found the correct page, but the chosen p. 3 excerpt begins after the strongest identification/fear lines. Reranking also allowed an irrelevant p. 9 passage into the evidence list.
- **OCR:** Not significant.
- **Prompt/output behavior:** V2 follows the requested Question/Response/Evidence format better than v1, but the response still under-synthesizes the retrieved evidence.

## Delta vs v1

**Mixed, slight improvement overall.** V1 retrieved only relevant p. 3 evidence and avoided irrelevant pages, but it mostly returned “Best evidence” rather than a real answer. V2 improves generation format by giving a direct answer sentence, but it is incomplete and retrieval/reranking worsens by adding irrelevant p. 9 evidence. Qwen appears to have improved answer formatting/safety, but not enough to answer the full question.

## Overall judgment

V2 is **partially correct but inadequate** for this simple factual lookup. A complete answer should say: Kalchas is Thestor’s son, a seer/bird-interpreter who knows Apollo’s will; he is afraid because revealing that Apollo’s anger comes from Agamemnon’s dishonouring of Chryses will anger Agamemnon, so Achilles promises to protect him.

## Q3. Why does Apollo send a plague against the Achaians?

**Test set:** A — Simple factual lookup

### Expected

- Expected evidence: pp. 1–3

- Good answer should mention: Agamemnon dishonoured Chryses and refused to return Chryseis; Apollo punishes the army.

- Failure signs: Says Achilles caused the plague; cites only later Achilles/Agamemnon quarrel pages.

### Investigator response \(v2 Ollama/Qwen\)

```md
Question: Why does Apollo send a plague against the Achaians?
Response: Apollo sends a plague against the Achaians because Agamemnon dishonored Chryses, a priest of Apollo.
Evidence:
- [p. 3 | iliad_book1_p0003_c01] 85 In the name of Apollo beloved of Zeus to whom you, Kalchas, make your prayers when you interpret the gods' will to the Danaans, no man so long as I am alive above earth and see daylight shall lay the weight of his hands on you beside the hollow ships, not one of all the Danaans, even if you mean Agamemnon, 90 who now claims to be far the greatest of all the Achaians.' At this the blameless seer took courage again and spoke forth: 'No, it is not for the sake of some vow or hecatomb he blames u...
- [p. 1 | iliad_book1_p0001_c01] Zeus' son and Leto's, Apollo, who in anger at the king drove the foul pestilence along the host, and the people perished, I0 since Atreus' son had dishonoured Chryses, priest of Apollo, when he came beside the fast ships of the Achaians to ransom back his daughter, carrying gifts beyond count and holding in his hands wound on a staff of gold the ribbons of Apollo who strikes from afar, and supplicated all the Achaians, 15 but above all Atreus' two sons, the marshals of the people: 'Sons of Atreu...
```

### Subagent evaluation

**Question:** Why does Apollo send a plague against the Achaians?  
**Expected pages:** pp. 1–3  
**Expected answer:** Agamemnon dishonoured Chryses, Apollo's priest, by refusing the ransom / refusing to return Chryseis; Apollo punishes the Achaian army.

## Lightweight checks

- **Expected-page coverage:** Pass/partial. The result cites **p. 1** and **p. 3**, both in the expected range. It still misses **p. 2**, which gives the clearest narrative sequence: Agamemnon drives Chryses away, Chryses prays, Apollo hears, and the plague begins.
- **Direct answer:** Pass. Unlike v1, v2 gives an actual response: "Apollo sends a plague ... because Agamemnon dishonored Chryses, a priest of Apollo."
- **Completeness:** Partial. The response captures the core cause, but does **not explicitly mention** Agamemnon's refusal to return Chryseis / accept ransom, which is part of the ideal answer. That detail is present in source p. 3 and implied on p. 1, but not synthesized in the answer sentence.
- **Forbidden failure signs:** Pass. It does **not** blame Achilles and does **not** rely only on later Achilles/Agamemnon quarrel pages.

## Source check

- **p. 1** directly says Apollo drove pestilence through the host because Atreus' son dishonoured Chryses, priest of Apollo, when Chryses came to ransom his daughter.
- **p. 2** supplies the strongest causal sequence: Agamemnon refuses, Chryses prays for Apollo's arrows to make the Danaans pay, Apollo hears and attacks the camp.
- **p. 3** gives Kalchas' explanation: Apollo blames them for Agamemnon's dishonouring of his priest and refusal to return the daughter or accept ransom.

## Rubric

| Criterion | Score | Notes |
|---|---:|---|
| retrieval_relevance | 4/5 | p. 1 and p. 3 are highly relevant; missing p. 2 loses the cleanest plague-action sequence. |
| citation_accuracy | 4/5 | Citations support the main claim. The p. 3 evidence snippet starts early and appears truncated around the most important explanation, but p. 1 is strong. |
| speaker_attribution | n/a | The answer does not need speaker attribution; no misattribution detected. |
| causal_chain | 4/5 | Correct core chain: Agamemnon dishonours Apollo's priest → Apollo sends plague. Slightly incomplete because refusal/ransom and Chryses' prayer are not stated in the final answer. |
| no_hallucination | 5/5 | No unsupported or invented claim detected. |
| answer_quality | 4/5 | Clear and direct, but a fuller answer should add that Agamemnon refused to return Chryseis / accept ransom. |

## Diagnosis

- **Generation/prompt:** Improved substantially. v2 answers the question directly instead of outputting only "Best evidence" snippets.
- **Retrieval/reranking:** Mostly adequate, but still not ideal. It retrieves relevant p. 1 and p. 3, while missing p. 2, the best source for the prayer-to-plague sequence. Snippet selection for p. 3 remains suboptimal because it begins with Achilles' reassurance to Kalchas and is truncated near the key cause.
- **OCR:** Not a blocker. Minor OCR artifacts such as `I0` / `I00` exist, but the relevant text is readable and sufficient.
- **Prompt/citation formatting:** Evidence remains somewhat bulky/truncated, but the final answer now synthesizes the retrieved material.

## V1 → V2 delta / Qwen judgment

**Qwen/v2 improved.** V1 retrieved similar relevant pages but failed at generation, giving an evidence dump rather than a direct answer. V2 keeps the grounding and adds a concise correct answer. Remaining weakness is completeness and retrieval/snippet selection, not factuality.

**Overall:** Good result for a simple factual lookup, with minor deductions for omitting the refusal/Chryseis detail and missing p. 2.

## Q4. Who asks Thetis to appeal to Zeus, and what does he want Zeus to do?

**Test set:** B — Speaker/action attribution

### Expected

- Expected evidence: pp. 11–12

- Good answer should mention: Achilles asks Thetis; he wants Zeus to help the Trojans and push the Achaians back so Agamemnon realizes his mistake.

- Failure signs: Says Thetis asks Achilles; says Achilles directly prays to Zeus; misses the purpose of punishing the Achaians.

### Investigator response \(v2 Ollama/Qwen\)

```md
Question: Who asks Thetis to appeal to Zeus, and what does he want Zeus to do?
Response: Thetis asks Zeus for help on p.
Evidence:
- [p. 3 | iliad_book1_p0003_c01] 85 In the name of Apollo beloved of Zeus to whom you, Kalchas, make your prayers when you interpret the gods' will to the Danaans, no man so long as I am alive above earth and see daylight shall lay the weight of his hands on you beside the hollow ships, not one of all the Danaans, even if you mean Agamemnon, 90 who now claims to be far the greatest of all the Achaians.' At this the blameless seer took courage again and spoke forth: 'No, it is not for the sake of some vow or hecatomb he blames u...
- [p. 14 | iliad_book1_p0014_c01] But when the twelfth dawn after this day appeared, the gods who live forever came back to Olympos all in a body and Zeus led them; nor did Thetis forget the entreaties 495 of her son, but she emerged from the sea's waves early in the morning and went up to the tall sky and Olympos.
- [p. 15 | iliad_book1_p0015_c01] 530 So these two who had made their plans separated, and Thetis leapt down again from shining Olympos into the sea's depth, but Zeus went back to his own house, and all the gods rose up from their chairs to greet the coming of their father, not one had courage to keep his place as the father advanced, but stood up to greet him.
```

### Subagent evaluation

**Question:** Who asks Thetis to appeal to Zeus, and what does he want Zeus to do?  
**Expected:** Achilles asks Thetis; he wants Zeus to help/strengthen the Trojans and drive/pin the Achaians back to their ships so Agamemnon recognizes his mistake/dishonor of Achilles.

## v2 response evaluated

> Thetis asks Zeus for help on p.

Cited evidence: p. 3, p. 14, p. 15.

## Source check

- **p. 11** has Achilles speaking to Thetis: “You then, if you have power to, protect your own son, going to Olympos and supplicating Zeus...”
- **p. 12** gives the requested outcome: Achilles tells Thetis to ask Zeus to “help the Trojans” and “pin the Achaians back against the ships and the water,” so Agamemnon may recognize “his madness” and that he dishonored “the best of the Achaians.”
- **p. 14** is related follow-through: Thetis does not forget “the entreaties of her son” and asks Zeus to honor Achilles by putting strength into the Trojans.
- **p. 15** only shows Zeus responding/agreeing and the aftermath; it is secondary evidence.
- **p. 3** is irrelevant to this question.

## Lightweight checks

- **Expected-page coverage:** Fail. The result misses both key pages, **pp. 11–12**.
- **Citation support:** Weak. p. 14 partly supports that Thetis later appeals to Zeus on her son’s behalf, but the cited snippet in the case stops before the main request. p. 15 is follow-up; p. 3 is off-target.
- **Forbidden failure signs:** Partial fail. It does not say “Thetis asks Achilles,” but it effectively answers the wrong action: “Thetis asks Zeus,” rather than identifying **Achilles** as the one who asks Thetis. It also omits the purpose of punishing/pinning back the Achaians so Agamemnon learns his error.

## Rubric

| Criterion | Score | Notes |
|---|---:|---|
| retrieval_relevance | 2/5 | Retrieves related p. 14 and p. 15, but misses direct request on pp. 11–12 and includes irrelevant p. 3. |
| citation_accuracy | 2/5 | Citations are real but do not adequately support the asked attribution or full purpose. |
| speaker_attribution | 1/5 | The answer misframes the question by naming Thetis as asker-to-Zeus instead of Achilles as asker-of-Thetis. |
| causal_chain | 1/5 | Omits Achilles’ desired chain: Zeus helps Trojans → Achaians suffer/are driven back → Agamemnon recognizes his dishonor of Achilles. |
| no_hallucination | 3/5 | “Thetis asks Zeus for help” is not invented, but it is not the answer to this question and is incomplete. |
| answer_quality | 1/5 | Fragmentary (“on p.”), indirect, and missing the central answer. |

## Diagnosis

- **Primary failure: retrieval/reranking.** The system did not surface pp. 11–12, where Achilles’ request and rationale are explicit. Reranking appears to prefer later Zeus/Thetis pages and a spurious Zeus match on p. 3.
- **Secondary failure: generation/prompt.** Unlike v1’s pure “Best evidence” dump, v2 attempts a prose answer, but it answers the wrong relation and trails off (“on p.”). The prompt/model did not enforce the exact “who asks Thetis” role structure.
- **OCR:** Not a meaningful cause. The relevant pp. 11–12 text is readable and accurate enough.

## Delta vs v1

Qwen/v2 is **worse overall for Q4**. v1 at least surfaced “entreaties of her son” on p. 14 and did not make a direct wrong-answer sentence, though it failed to synthesize. v2 produces a shorter answer, but it is fragmentary and incorrectly centered on Thetis asking Zeus rather than Achilles asking Thetis. Retrieval remains similarly weak because pp. 11–12 are still missing.

## Overall judgment

**Inadequate / failed.** A correct answer should say: **Achilles asks his mother Thetis to appeal to Zeus; he wants Zeus to help the Trojans drive the Achaians back to their ships so Agamemnon realizes he dishonored Achilles.**

## Q5. What does Thetis ask Zeus to do for Achilles?

**Test set:** B — Speaker/action attribution

### Expected

- Expected evidence: pp. 14–15

- Good answer should mention: Thetis asks Zeus to honour Achilles by giving strength to the Trojans until the Achaians restore Achilles’ honour.

- Failure signs: Says Thetis asks Zeus to return Briseis; says Zeus helps Achilles fight directly.

### Investigator response \(v2 Ollama/Qwen\)

```md
Question: What does Thetis ask Zeus to do for Achilles?
Response: did not forget the entreaties of her son," but it does not specify what those entreaties were.
Evidence:
- [p. 14 | iliad_book1_p0014_c01] But when the twelfth dawn after this day appeared, the gods who live forever came back to Olympos all in a body and Zeus led them; nor did Thetis forget the entreaties 495 of her son, but she emerged from the sea's waves early in the morning and went up to the tall sky and Olympos.
- [p. 15 | iliad_book1_p0015_c01] 530 So these two who had made their plans separated, and Thetis leapt down again from shining Olympos into the sea's depth, but Zeus went back to his own house, and all the gods rose up from their chairs to greet the coming of their father, not one had courage to keep his place as the father advanced, but stood up to greet him.
- [p. 8 | iliad_book1_p0008_c01] Even 280 though you are the stronger man, and the mother who bore you was immortal, yet is this man greater who is lord over more than you rule: Son of Atreus, give up your anger; even I entreat you to give over your bitterness against Achilleus, he who stands as a great bulwark of battle over all the Achaians.' Then in answer again spoke powerful Agamemnon: 285 'Yes, old sir, all this you have said is fair and orderly.
```

### Subagent evaluation

**Question:** What does Thetis ask Zeus to do for Achilles?  
**Expected evidence:** pp. 14–15  
**Expected answer:** Thetis asks Zeus to honour Achilles by strengthening/helping the Trojans until the Achaians restore Achilles’ rights/honour.

## v2 response assessed

> did not forget the entreaties of her son," but it does not specify what those entreaties were.

Citations shown: p. 14, p. 15, p. 8.

## Lightweight checks

- **Expected-page coverage:** Partial. The result cites **p. 14** and **p. 15**, the expected pages, but the displayed p. 14 excerpt stops before the actual answer-bearing lines.
- **Key answer span missing:** Yes. Page 14 clearly contains Thetis’ request: “Now give honour to my son…” and “put strength into the Trojans, until the Achaians give my son his rights, and his honour is increased among them.” This was not included in the cited excerpt.
- **Irrelevant evidence:** Yes. **p. 8** is unrelated to Thetis’ appeal to Zeus.
- **Forbidden failure signs:** Not present. It does not say Thetis asks Zeus to return Briseis and does not say Zeus helps Achilles fight directly.
- **False negative:** Yes. The response claims the evidence does not specify the entreaties, but the source page does specify them just below the cited p. 14 excerpt.

## Rubric scores

| Criterion | Score | Notes |
|---|---:|---|
| retrieval_relevance | 2/5 | Broad page retrieval finds p. 14–15, but chunk/snippet selection misses the decisive lines; p. 8 is noise. |
| citation_accuracy | 2/5 | Citations are real, but they do not support the answer and omit the main supporting passage. |
| speaker_attribution | 2/5 | It correctly associates Thetis with her son’s entreaties, but does not state her actual request to Zeus. |
| causal_chain | 1/5 | It misses the required chain: Achilles dishonoured → Thetis asks Zeus to honour him → Trojans strengthened until Achaians restore honour. |
| no_hallucination | 3/5 | No invented event, but the “does not specify” claim is an unsupported/incorrect conclusion against the source. |
| answer_quality | 1/5 | Fails to answer the question; gives an incorrect insufficiency answer. |

## Diagnosis

- **Primary failure: retrieval/chunking/reranking.** The system reaches the right page but selects a chunk that ends immediately before Thetis’ actual request. This is a near-miss span-selection failure.
- **Secondary failure: generation.** The model treats incomplete retrieved evidence as proof that the source does not specify the answer, instead of answering from the expected page context or signaling uncertainty more cautiously.
- **Prompt issue:** The prompt likely needs a guardrail against saying “not specified” when adjacent source context may contain the answer, and should require direct answer extraction from cited evidence.
- **OCR:** Not a blocker. The relevant text is readable despite minor OCR line-number artifacts (`sos`, `51o`).

## Delta vs v1

- **v1:** Mostly an evidence dump; it retrieved p. 14–15 but did not synthesize the answer.
- **v2/Qwen:** Slightly better format because it attempts a prose response, but **substantively worse** because it asserts the answer is not specified. The retrieval problem remains essentially the same: correct page, wrong span, plus irrelevant third citation.

## Overall judgment

**Failed / near miss.** v2 found the expected page range but missed the crucial lines and generated an incorrect “not specified” answer. Correct response should be: **Thetis asks Zeus to honour Achilles by giving strength to the Trojans until the Achaians restore/increase Achilles’ honour.**

## Q6. What does Hera suspect Zeus has done?

**Test set:** B — Speaker/action attribution

### Expected

- Expected evidence: p. 16

- Good answer should mention: Hera suspects Zeus was persuaded by Thetis to honour Achilles and harm the Achaians.

- Failure signs: Attributes Hera’s suspicion to Achilles; says Achilles criticizes Zeus.

### Investigator response \(v2 Ollama/Qwen\)

```md
Question: What does Hera suspect Zeus has done?
Response: Hera suspects that Zeus has been plotting with Thetis. This is evident from her statement on page 15: "Treacherous one, what god has been plotting counsels with you?"
Evidence:
- [p. 3 | iliad_book1_p0003_c01] 85 In the name of Apollo beloved of Zeus to whom you, Kalchas, make your prayers when you interpret the gods' will to the Danaans, no man so long as I am alive above earth and see daylight shall lay the weight of his hands on you beside the hollow ships, not one of all the Danaans, even if you mean Agamemnon, 90 who now claims to be far the greatest of all the Achaians.' At this the blameless seer took courage again and spoke forth: 'No, it is not for the sake of some vow or hecatomb he blames u...
- [p. 1 | iliad_book1_p0001_c01] ONE BOOK S ING, goddess, the anger of Peleus' son Achilleus and its devastation, which put pains thousandfold upon the Achaians, hurled in their multitudes to the house of Hades strong souls of heroes, but gave their bodies to be the delicate feasting of dogs, of all birds, and the will of Zeus was accomplished 5 since that time when first there stood in division of conflict Atreus' son the lord of men and brilliant Achilleus.
- [p. 15 | iliad_book1_p0015_c01] 535 Thus he took his place on the throne; yet Hera was not ignorant, having seen how he had been plotting counsels with Thetis the silver-footed, the daughter of the sea's ancient, and at once she spoke revilingly to Zeus son of Kronos: 'Treacherous one, what god has been plotting counsels with you?
```

### Subagent evaluation

**Question:** What does Hera suspect Zeus has done?  
**Expected page:** p. 16  
**Expected answer:** Hera suspects that Zeus has been won over/persuaded by Thetis to honor Achilles and destroy or harm many Achaians beside their ships.

## v2 response under review

> Hera suspects that Zeus has been plotting with Thetis. This is evident from her statement on page 15: "Treacherous one, what god has been plotting counsels with you?"

Evidence returned: p. 3, p. 1, p. 15.

## Source check

- **p. 15** is relevant setup: the narrator says Hera saw Zeus “plotting counsels with Thetis,” and Hera asks Zeus who has been plotting with him.
- **p. 16** contains the actual answer-bearing suspicion: Hera says she is afraid Zeus “were won over by Thetis,” and thinks he nodded assent “to do honour to Achilleus, and to destroy many beside the ships of the Achaians.”
- **p. 1 and p. 3** are irrelevant or only broadly Zeus/Apollo-related noise for this question.

## Rubric scores

| Criterion | Score | Notes |
|---|---:|---|
| retrieval_relevance | 2/5 | v2 retrieves p. 15, which is adjacent and partially relevant, but misses the expected p. 16 span that directly answers the question. p. 1 and p. 3 are noise. |
| citation_accuracy | 2/5 | The p. 15 citation supports “plotting with Thetis,” but not Hera’s fuller suspicion about being won over to honor Achilles and harm the Achaians. |
| speaker_attribution | 4/5 | Correctly attributes the suspicion to Hera about Zeus/Thetis; no Achilles-misattribution failure. |
| causal_chain | 2/5 | Captures Zeus + Thetis plotting, but omits the key causal purpose: honor Achilles by damaging the Achaians. |
| no_hallucination | 4/5 | The answer is grounded in p. 15 and not fabricated, but incomplete and slightly under-specified as merely “plotting.” |
| answer_quality | 3/5 | Unlike v1, v2 gives a direct answer. However, it is incomplete because it stops before the main content of Hera’s suspicion on p. 16. |

## Diagnosis

- **Retrieval/reranking:** Main remaining weakness. The system should have ranked p. 16 above p. 1/p. 3 because p. 16 contains “won over by Thetis,” “honour Achilleus,” and “destroy many beside the ships of the Achaians.” Reranking still appears too influenced by generic Zeus/Apollo/early-book matches.
- **Generation:** Improved over v1 because it synthesizes a prose answer instead of only listing “Best evidence.” But generation did not infer or seek the adjacent continuation on p. 16, so the final answer is only half correct.
- **Prompt:** Better direct-answer behavior, but still needs pressure to include all requested action/attribution details and cite the strongest answer span, not just the first adjacent clue.
- **OCR:** Not a blocker. p. 16 has minor OCR noise (`SSS`, `goddcss`, `werc`), but the crucial wording is readable.

## Brief v1 comparison

v1 retrieved p. 16 but the displayed p. 16 chunk started too late, after Hera’s decisive accusation, and v1 failed generation by outputting evidence snippets instead of an answer. v2/Qwen **improves generation and speaker attribution** by answering directly and correctly naming Hera, Zeus, and Thetis. However, v2 **worsens retrieval/evidence coverage** because it does not retrieve/cite p. 16 at all and therefore misses the Achilles/Achaians portion of the answer.

## Overall judgment

**Score: 3/5 overall.** Qwen/v2 is a clear generation improvement over v1 for this case, but it remains incomplete: the correct full answer is that Hera suspects Zeus was persuaded by Thetis to honor Achilles and bring destruction on the Achaians at their ships.

## Q7. Trace the chain of events from Chryses’ request to Achilles’ withdrawal from the fighting.

**Test set:** C — Cause-and-effect chain

### Expected

- Expected evidence: pp. 1–12

- Good answer should mention: 1. Chryses asks for daughter back. 2. Agamemnon refuses. 3. Apollo sends plague. 4. Kalchas explains cause. 5. Agamemnon demands compensation. 6. Agamemnon takes Briseis. 7. Achilles withdraws and appeals to Thetis.

- Failure signs: Skips Kalchas; skips Briseis; treats Achilles’ withdrawal as random anger.

### Investigator response \(v2 Ollama/Qwen\)

```md
Question: Trace the chain of events from Chryses’ request to Achilles’ withdrawal from the fighting.
Response: Chryses, Apollo's priest, came to the Achaian camp to ransom his daughter Briseis, carrying numerous gifts (p.
Evidence:
- [p. 9 | iliad_book1_p0009_c01] But Agamemnon did not give up his anger and the first threat he made to Achilleus, but to Talthybios he gave his orders and Eurybates 320 who were heralds and hard-working henchmen to him: 'Go now to the shelter of Peleus' son Achilleus, to bring back Briseis of the fair cheeks leading her by the hand.
- [p. 11 | iliad_book1_p0011_c01] Then Chryses, priest of him who strikes from afar, Apollo, 370 came beside the fast ships of the bronze-armoured Achaians to ransom back his daughter, carrying gifts beyond count and holding in his hands wound on a staff of gold the ribbons of Apollo who strikes from afar, and supplicated all the Achaians, but above all Atreus' two sons, the marshals of the people.
- [p. 5 | iliad_book1_p0005_c01] I40 Come, now, we must haul a black ship down to the bright sea, and assemble rowers enough for it, and put on board it the hecatomb, and the girl herself, Chryseis of the fair cheeks, and let there be one responsible man in charge of her, either Aias or Idomeneus or brilliant Odysseus, 145 or you yourself, son of Peleus, most terrifying of all men, to reconcile by accomplishing sacrifice the archer.' Then looking darkly at him Achilleus of the swift feet spoke: 'O wrapped in shamelessness, with...
```

### Subagent evaluation

**Question:** Trace the chain of events from Chryses’ request to Achilles’ withdrawal from the fighting.  
**Expected pages:** pp. 1–12  
**v2 cited pages:** p. 9, p. 11, p. 5

## Verdict

**Score: 1/5 overall.** v2 retrieves some relevant pieces, including a very useful later recap on p. 11 and Briseis evidence on p. 9, but the generated answer is essentially unusable: it is truncated after one sentence and incorrectly says Chryses came to ransom his daughter **Briseis**. The correct daughter is **Chryseis**; Briseis is Achilles’ prize later taken by Agamemnon.

## Expected chain from source

1. Chryses, Apollo’s priest, comes with ransom to recover **Chryseis** (pp. 1, 11).
2. Agamemnon refuses and drives him away (pp. 1–2, 11).
3. Chryses prays; Apollo sends plague on the Achaians (p. 2; recap p. 11).
4. Achilles calls an assembly; Kalchas explains Apollo is angry because Agamemnon dishonoured Chryses and refused ransom (pp. 2–3; recap p. 11).
5. Agamemnon agrees to return Chryseis but demands compensation/a replacement prize (pp. 4–5).
6. Agamemnon threatens and then orders/takes Achilles’ Briseis (pp. 6, 9–10).
7. Achilles gives her up, withdraws in grief/anger, and appeals to Thetis to ask Zeus to punish the Achaians until Agamemnon recognizes his error (pp. 10–12).

## Rubric

| Criterion | Score | Notes |
| --- | ---: | --- |
| retrieval_relevance | 3/5 | Better than v1 in that p. 9 gives direct Briseis evidence and p. 5 catches part of the compensation dispute. p. 11 is also a strong recap. But the set still misses crucial direct pages: p. 2 plague, p. 3 Kalchas, p. 4 Agamemnon’s compensation demand, p. 10 Achilles’ withdrawal/calling Thetis, and p. 12 Thetis/Zeus request. |
| citation_accuracy | 2/5 | The evidence snippets themselves are page-correct, but the answer’s only substantive claim misuses them by saying Chryses’ daughter is Briseis. The citations do not support that claim. |
| speaker_attribution | 1/5 | The answer does not distinguish Chryses/Chryseis/Briseis, Agamemnon, Kalchas, Achilles, or Thetis. p. 11 is Achilles’ retrospective speech to Thetis, but the response does not identify that. |
| causal_chain | 1/5 | The chain is not traced. Only the opening event is attempted, and it is wrong/incomplete. Required steps involving Kalchas, compensation, Briseis, withdrawal, and Thetis are absent from the response. |
| no_hallucination | 2/5 | There is a serious generated factual error: Chryses ransoms Chryseis, not Briseis. Otherwise the response is mostly omission/truncation rather than invented narrative. |
| answer_quality | 0/5 | The response stops mid-citation/parenthesis and gives no usable ordered explanation. |

## Diagnosis

- **Retrieval:** Partial. v2 retrieved relevant pages but not a sufficient contiguous chain. The strongest retrieved item is p. 11, which actually contains a compact recap of much of the requested sequence, but p. 10–12 are needed for withdrawal/Thetis and p. 3 for Kalchas.
- **Reranking/snippet selection:** Mixed. Reranking improved over v1 by elevating p. 9 and p. 5, but it still underweighted event coverage across the full chain and omitted key pages. It should prioritize coverage of entities/events: Chryses/Chryseis, plague, Kalchas, compensation/prize, Briseis, Achilles/Thetis/Zeus.
- **Generation:** Primary failure. Qwen attempted a prose answer but produced a truncated, wrong first sentence and failed to use the retrieved evidence to synthesize the sequence.
- **OCR:** Not the main issue. OCR has minor noise (`Briseus' daughter`, line-number artifacts, occasional `takc/hcrc`), but the source is readable enough. The Chryseis/Briseis error is a generation/context failure, not an unavoidable OCR problem.
- **Prompt:** Still needs stronger instructions for multi-hop questions: require an ordered chain, prohibit stopping after a fragment, and add a checklist that Kalchas, Briseis, withdrawal, and Thetis are included.

## v1 comparison / Qwen effect

Compared with v1, **retrieval is slightly improved**: v1 cited p. 1, p. 8, and p. 11, with p. 8 mostly marginal; v2 cites p. 9 and p. 5, which are more useful for the Briseis/compensation part. However, **generation worsened**. v1 was an evidence dump with no synthesized answer, but it did not introduce a major wrong claim. v2 tries to answer and immediately confuses Chryseis with Briseis, then truncates. Net result: **Qwen/v2 worsened answer quality for Q7 despite modest retrieval improvement.**

## Q8. How does the quarrel between Achilles and Agamemnon move from a dispute over Chryseis to a dispute over Briseis?

**Test set:** C — Cause-and-effect chain

### Expected

- Expected evidence: pp. 3–10

- Good answer should mention: Agamemnon must return Chryseis but demands another prize; he threatens/takes Briseis from Achilles as compensation.

- Failure signs: Says Briseis belongs to Agamemnon originally; says Achilles takes Chryseis.

### Investigator response \(v2 Ollama/Qwen\)

```md
Question: How does the quarrel between Achilles and Agamemnon move from a dispute over Chryseis to a dispute over Briseis?
Response: In response, the seer Kalchas states that Agamemnon is not motivated by a vow or sacrifice but rather by his dishonoring of Chryses and refusing to release his daughter, Briseis.
Evidence:
- [p. 8 | iliad_book1_p0008_c01] Even 280 though you are the stronger man, and the mother who bore you was immortal, yet is this man greater who is lord over more than you rule: Son of Atreus, give up your anger; even I entreat you to give over your bitterness against Achilleus, he who stands as a great bulwark of battle over all the Achaians.' Then in answer again spoke powerful Agamemnon: 285 'Yes, old sir, all this you have said is fair and orderly.
- [p. 3 | iliad_book1_p0003_c01] 85 In the name of Apollo beloved of Zeus to whom you, Kalchas, make your prayers when you interpret the gods' will to the Danaans, no man so long as I am alive above earth and see daylight shall lay the weight of his hands on you beside the hollow ships, not one of all the Danaans, even if you mean Agamemnon, 90 who now claims to be far the greatest of all the Achaians.' At this the blameless seer took courage again and spoke forth: 'No, it is not for the sake of some vow or hecatomb he blames u...
```

### Subagent evaluation

**Question:** How does the quarrel between Achilles and Agamemnon move from a dispute over Chryseis to a dispute over Briseis?  
**Expected evidence:** pp. 3–10  
**Expected answer:** Kalchas explains that Apollo's plague will not stop until Agamemnon returns Chryseis. Agamemnon agrees, but demands another prize so he will not be left without honor/compensation. Achilles objects that the prizes have already been distributed. Agamemnon then threatens to take another leader's prize and explicitly chooses Achilles' Briseis, later sending heralds to take her.

## v2 result summary

The v2/Ollama response says:

> “Kalchas states that Agamemnon is not motivated by a vow or sacrifice but rather by his dishonoring of Chryses and refusing to release his daughter, Briseis.”

Citations returned: **p. 8** and **p. 3**.

This is not an adequate answer. It identifies an early cause of the plague, but it does not explain how the dispute shifts to Briseis. It also makes a serious name/entity error: Chryses' daughter is **Chryseis**, not Briseis.

## Source check

Key source passages the answer needed:

- **p. 3:** Kalchas says Apollo is angry because Agamemnon dishonored Chryses and would not return his daughter; the girl must be returned without ransom.
- **p. 4:** Agamemnon says he is willing to give Chryseis back, but demands another prize because his own prize is going elsewhere; he threatens to take Achilles', Aias', or Odysseus' prize.
- **p. 5:** Achilles objects that the spoils have already been distributed and accuses Agamemnon of threatening to strip away his prize.
- **p. 6:** Agamemnon gives the explicit bridge: “Even as Phoibos Apollo is taking away my Chryseis ... I shall take the fair-cheeked Briseis, your prize.”
- **pp. 9–10:** Agamemnon sends heralds to take Briseis, and Patroklos hands her over.

The v2 evidence includes p. 3 background and p. 8 mediation, but misses the decisive transition pages, especially **p. 4** and **p. 6**.

## Rubric scores

| Criterion | Score | Notes |
|---|---:|---|
| retrieval_relevance | 2/5 | p. 3 is relevant background for Chryseis; p. 8 is only indirect quarrel/mediation context. The strongest pages for the Chryseis-to-Briseis transition, pp. 4 and 6, are absent, as are the actual seizure pages pp. 9–10. |
| citation_accuracy | 1/5 | The p. 3 citation supports “not vow/hecatomb” and dishonoring Chryses, but it does **not** support calling the daughter Briseis. p. 8 does not support the stated answer. |
| speaker_attribution | 2/5 | Kalchas is correctly associated with the p. 3 explanation, but the response wrongly makes his explanation into the answer to the Briseis transition and attributes a Briseis claim he does not make. |
| causal_chain | 0/5 | The required chain is missing: return Chryseis → Agamemnon demands replacement prize → Achilles objects → Agamemnon threatens/takes Briseis. |
| no_hallucination | 1/5 | The answer introduces a major unsupported/entity-confusion claim by saying Chryses' daughter is Briseis. |
| answer_quality | 1/5 | It is a short prose answer rather than just an evidence dump, but it answers the wrong part of the story and omits the central compensation/prize logic. |

## Diagnosis

- **Retrieval/reranking:** Major failure. Reranking appears to have overvalued early lexical matches around Kalchas, “vow/hecatomb,” “dishonoured,” and general quarrel context, while failing to surface the explicit bridge sentence on p. 6 and the replacement-prize demand on p. 4.
- **Generation:** Major failure. Qwen generated a fluent sentence, but it compressed the wrong evidence into an incorrect answer and confused Chryseis with Briseis.
- **Prompt:** The prompt likely still does not force a stepwise causal chain with evidence for each transition. A chain question should require the model to account for both named women and the prize/compensation mechanism.
- **OCR:** Not the main issue. OCR on p. 6 has minor artifacts (`takc`, `hcr`, `Briscis`), but the relevant sentence remains readable enough: Apollo takes Chryseis; Agamemnon will take Briseis, Achilles' prize.

## v1 comparison / Qwen change

**v1 for Q8 was also poor**, because it mostly returned evidence snippets and did not synthesize the chain. However, v1 retrieved **p. 9**, which at least showed Agamemnon ordering Briseis taken. v2 instead retrieves **p. 3** and **p. 8**, missing even that endpoint.

Overall, **Qwen/v2 worsened for this question**: it improved the surface form by producing a prose response, but retrieval coverage is weaker and generation introduces a serious Chryseis/Briseis hallucination. The net result is worse than v1.

## Q9. Why does Achilles believe Agamemnon has dishonoured him?

**Test set:** C — Cause-and-effect chain

### Expected

- Expected evidence: pp. 5–12

- Good answer should mention: Achilles fights for Agamemnon/Menelaos’ cause, yet Agamemnon takes his prize; Briseis represents honour/status.

- Failure signs: Says Achilles is angry only because he loves Briseis romantically; misses honour/prize logic.

### Investigator response \(v2 Ollama/Qwen\)

```md
Question: Why does Achilles believe Agamemnon has dishonoured him?
Response: Best evidence:
- [p. 3] 85 In the name of Apollo beloved of Zeus to whom you, Kalchas, make your prayers when you interpret the gods' will to the Danaans, no man so long as I am alive above earth and see daylight shall lay the weight of his hands on you beside the...
- [p. 1] Zeus' son and Leto's, Apollo, who in anger at the king drove the foul pestilence along the host, and the people perished, I0 since Atreus' son had dishonoured Chryses, priest of Apollo, when he came beside the fast ships of the Achaians to...
Evidence:
- [p. 3 | iliad_book1_p0003_c01] 85 In the name of Apollo beloved of Zeus to whom you, Kalchas, make your prayers when you interpret the gods' will to the Danaans, no man so long as I am alive above earth and see daylight shall lay the weight of his hands on you beside the hollow ships, not one of all the Danaans, even if you mean Agamemnon, 90 who now claims to be far the greatest of all the Achaians.' At this the blameless seer took courage again and spoke forth: 'No, it is not for the sake of some vow or hecatomb he blames u...
- [p. 1 | iliad_book1_p0001_c01] Zeus' son and Leto's, Apollo, who in anger at the king drove the foul pestilence along the host, and the people perished, I0 since Atreus' son had dishonoured Chryses, priest of Apollo, when he came beside the fast ships of the Achaians to ransom back his daughter, carrying gifts beyond count and holding in his hands wound on a staff of gold the ribbons of Apollo who strikes from afar, and supplicated all the Achaians, 15 but above all Atreus' two sons, the marshals of the people: 'Sons of Atreu...
```

### Subagent evaluation

**Question:** Why does Achilles believe Agamemnon has dishonoured him?  
**Expected evidence:** pp. 5–12  
**Expected answer:** Achilles says he has been fighting for Agamemnon/Menelaos’ honour even though the Trojans have not personally wronged him; Agamemnon then threatens/takes Briseis, Achilles’ awarded prize, which publicly strips Achilles of honour/status.

## v2 response assessed

The response gives only “Best evidence” snippets from **p. 3** and **p. 1**, both about Apollo/Chryses/Kalchas and Agamemnon dishonouring **Chryses**, not Achilles.

## Lightweight checks

- **Expected-page coverage:** Fail. No evidence from pp. 5–12 is cited.
- **Key answer span missing:** Yes. It misses:
  - **p. 5:** Achilles says he fights for Agamemnon/Menelaos’ honour and that Agamemnon now threatens to strip away his prize.
  - **p. 6:** Agamemnon explicitly says he will take Briseis, Achilles’ prize, to show he is greater.
  - **p. 10:** Achilles says Agamemnon has dishonoured him by taking and keeping his prize.
  - **pp. 11–12:** Achilles retells the causal chain to Thetis and says Agamemnon did no honour to the best of the Achaians.
- **Irrelevant evidence:** Yes. p. 1 and p. 3 are background to the plague and Chryses episode, not Achilles’ own grievance.
- **Forbidden failure signs:** It does not falsely reduce Achilles’ anger to romantic love for Briseis, but it also fails to explain the honour/prize logic.

## Rubric scores

| Criterion | Score | Notes |
|---|---:|---|
| retrieval_relevance | 1/5 | Retrieved passages are about Chryses/Kalchas/Apollo, not Achilles’ claim that Agamemnon dishonoured him. |
| citation_accuracy | 2/5 | Citations are real, but they do not support the asked answer; they support a different “dishonoured” episode. |
| speaker_attribution | n/a | The response does not synthesize claims about Achilles’ belief or speakers. |
| causal_chain | 0/5 | Completely misses the needed chain: Achilles fights for Agamemnon/Menelaos → receives Briseis as prize/status → Agamemnon takes her → Achilles is publicly dishonoured. |
| no_hallucination | 4/5 | No invented claims, but the evidence selection is misleading because it points to Chryses’ dishonour instead of Achilles’. |
| answer_quality | 1/5 | Evidence dump only; no direct answer and no central honour/prize explanation. |

## Diagnosis

- **Primary failure: retrieval/reranking.** The system appears to overmatch the lexical term “dishonoured” and retrieves early passages where Agamemnon dishonours Chryses, instead of later passages where Achilles says Agamemnon dishonoured him.
- **Secondary failure: generation/prompt.** The generator does not notice that the cited evidence is about the wrong person and still emits a best-evidence list rather than saying evidence is insufficient or producing a sourced answer.
- **Prompt issue:** The prompt likely still rewards returning top evidence over answering the question. It needs an entity/claim check: “dishonoured him” must resolve to Achilles, not Chryses.
- **OCR:** Not a major blocker. Relevant pp. 5–12 are readable; p. 6 has minor OCR noise (`takc`, `hcr`, `Briscis`) but enough signal remains for retrieval if reranking/query expansion used terms like “prize,” “Briseis,” and “honour.”

## Delta vs v1

- **v1:** Failed in the same way: p. 1 and p. 3 evidence dump about Chryses/Kalchas, no pp. 5–12, no synthesized answer.
- **v2/Qwen:** **No improvement; effectively unchanged.** Qwen did not improve generation for this case because the output remains an evidence dump, and retrieval/reranking still selects the wrong “dishonoured” episode.

## Overall judgment

**Failed.** v2 does not answer why Achilles believes he was dishonoured. Correct answer should cite pp. 5–6 and/or p. 10: Achilles fought for Agamemnon and Menelaos’ cause, did much of the fighting, received Briseis as his prize, and Agamemnon’s seizure of that prize publicly denied his honour.

## Q10. What is ironic about Achilles asking Zeus to help the Trojans?

**Test set:** D — Interpretive but source-grounded

### Expected

- Expected evidence: pp. 5, 12, 14–16

- Good answer should mention: Achilles is an Achaian warrior who fought against Troy, but because Agamemnon dishonoured him, he wants Trojan success so the Achaians suffer and recognize his value.

- Failure signs: Says Thetis asks Achilles to pray; says the irony is Zeus being suspicious; cites irrelevant p. 13.

### Investigator response \(v2 Ollama/Qwen\)

```md
Question: What is ironic about Achilles asking Zeus to help the Trojans?
Response: On page 8, Thetis appeals to Zeus to persuade Agamemnon to give up his anger against Achilles, who stands as a bulwark for the Achaians.
Evidence:
- [p. 3 | iliad_book1_p0003_c01] 85 In the name of Apollo beloved of Zeus to whom you, Kalchas, make your prayers when you interpret the gods' will to the Danaans, no man so long as I am alive above earth and see daylight shall lay the weight of his hands on you beside the hollow ships, not one of all the Danaans, even if you mean Agamemnon, 90 who now claims to be far the greatest of all the Achaians.' At this the blameless seer took courage again and spoke forth: 'No, it is not for the sake of some vow or hecatomb he blames u...
- [p. 15 | iliad_book1_p0015_c01] 530 So these two who had made their plans separated, and Thetis leapt down again from shining Olympos into the sea's depth, but Zeus went back to his own house, and all the gods rose up from their chairs to greet the coming of their father, not one had courage to keep his place as the father advanced, but stood up to greet him.
- [p. 8 | iliad_book1_p0008_c01] Even 280 though you are the stronger man, and the mother who bore you was immortal, yet is this man greater who is lord over more than you rule: Son of Atreus, give up your anger; even I entreat you to give over your bitterness against Achilleus, he who stands as a great bulwark of battle over all the Achaians.' Then in answer again spoke powerful Agamemnon: 285 'Yes, old sir, all this you have said is fair and orderly.
```

### Subagent evaluation

**Question:** What is ironic about Achilles asking Zeus to help the Trojans?  
**Expected evidence:** pp. 5, 12, 14–16  
**Expected answer:** Achilles is an Achaian warrior fighting against Troy, but after Agamemnon dishonours him, he wants Zeus to give the Trojans success so the Achaians suffer and recognize Achilles' value.

## v2 response assessed

The v2 answer says: "On page 8, Thetis appeals to Zeus to persuade Agamemnon to give up his anger against Achilles, who stands as a bulwark for the Achaians."

This is substantially wrong. Page 8 is Nestor urging Agamemnon to give up anger and describing Achilles as a bulwark; it is not Thetis appealing to Zeus. The answer also does not identify the irony: Achilles, an Achaian champion, seeks Trojan success against his own side because of Agamemnon's dishonour.

## Source check

- **p. 5:** Achilles says he did not come to fight because the Trojans harmed him; he came for Agamemnon/Menelaos' honour, and now Agamemnon dishonours him by threatening his prize. This establishes the ironic contrast.
- **p. 12:** Achilles tells Thetis to ask Zeus to help the Trojans and drive the Achaians back to the ships so Agamemnon recognizes his madness and failure to honour the best Achaian.
- **p. 14:** Thetis actually supplicates Zeus, asking him to strengthen the Trojans until the Achaians restore Achilles' honour.
- **pp. 15–16:** Zeus assents; Hera understands this as honouring Achilles and destroying many Achaians.
- **p. 8:** Relevant only indirectly: Nestor calls Achilles a bulwark for the Achaians. It does not contain Thetis or Zeus.

## Rubric scores

| Criterion | Score | Rationale |
|---|---:|---|
| retrieval_relevance | 2/5 | Retrieved p. 15, which is relevant to Zeus's assent, but also retrieved p. 3 and p. 8, while missing crucial pp. 5, 12, 14, and 16. |
| citation_accuracy | 1/5 | The evidence snippets themselves are real, but the answer's main citation claim is inaccurate: p. 8 is not Thetis appealing to Zeus. |
| speaker_attribution | 0/5 | Major misattribution: Nestor's page-8 speech is treated as Thetis appealing to Zeus. |
| causal_chain | 1/5 | It does not explain Agamemnon dishonouring Achilles -> Achilles asks Thetis/Zeus -> Trojan success harms Achaians -> Achilles' value is recognized. |
| no_hallucination | 1/5 | The claim that Thetis appeals to Zeus on p. 8 to persuade Agamemnon is unsupported and conflates separate passages. |
| answer_quality | 0/5 | Does not answer the interpretive question and gives a false summary of the evidence. |

## Diagnosis

- **Primary failure: generation.** The generator conflates p. 8's Nestor passage with the Thetis/Zeus appeal and produces an unsupported answer. This is worse than merely failing to synthesize.
- **Secondary failure: retrieval/reranking.** The retrieval set lacks the most important evidence, especially p. 12 for Achilles' request and p. 5 for why it is ironic. Page 15 alone is not enough; p. 8 is only tangential; p. 3 is irrelevant.
- **OCR:** Not a meaningful cause. The relevant source pages are readable enough; minor OCR artifacts do not explain the misattribution.
- **Prompt:** The prompt still does not force a grounded answer tied to cited snippets, and it allows the model to infer across snippets incorrectly rather than verify speaker/action attribution.

## Comparison with v1

v1 was flawed but better. It retrieved pp. 12, 14, and 15 and avoided forbidden claims, but mostly returned "Best evidence" rather than a synthesized answer. v2 gives a prose answer, but the prose is wrong: it misattributes p. 8 to Thetis/Zeus and misses the core irony. Therefore, **Qwen/v2 worsened Q10 overall**: generation became more fluent but less faithful, and retrieval/reranking also regressed by losing p. 12 and p. 14.

## Overall judgment

**Score: poor/failing.** v2 does not answer the question and introduces a serious attribution hallucination. The needed answer is: Achilles is one of the Achaians' greatest fighters against Troy, so it is ironic that he asks Zeus to help the Trojans; he does this because Agamemnon has dishonoured him, and he wants the Achaians to suffer until they recognize his worth.

## Q11. How does Book 1 show that honour is both personal and political?

**Test set:** D — Interpretive but source-grounded

### Expected

- Expected evidence: pp. 1–16

- Good answer should mention: Personal insult to Chryses causes public plague; Agamemnon’s seizure of Briseis humiliates Achilles; Achilles’ anger harms the whole army; Thetis/Zeus turn the honour dispute into a war-level consequence.

- Failure signs: Only discusses Achilles’ emotions; ignores public/military consequences.

### Investigator response \(v2 Ollama/Qwen\)

```md
Question: How does Book 1 show that honour is both personal and political?
Response: Best evidence:
- [p. 1] Zeus' son and Leto's, Apollo, who in anger at the king drove the foul pestilence along the host, and the people perished, I0 since Atreus' son had dishonoured Chryses, priest of Apollo, when he came beside the fast ships of the Achaians to...
- [p. 3] 85 In the name of Apollo beloved of Zeus to whom you, Kalchas, make your prayers when you interpret the gods' will to the Danaans, no man so long as I am alive above earth and see daylight shall lay the weight of his hands on you beside the...
Evidence:
- [p. 1 | iliad_book1_p0001_c01] Zeus' son and Leto's, Apollo, who in anger at the king drove the foul pestilence along the host, and the people perished, I0 since Atreus' son had dishonoured Chryses, priest of Apollo, when he came beside the fast ships of the Achaians to ransom back his daughter, carrying gifts beyond count and holding in his hands wound on a staff of gold the ribbons of Apollo who strikes from afar, and supplicated all the Achaians, 15 but above all Atreus' two sons, the marshals of the people: 'Sons of Atreu...
- [p. 3 | iliad_book1_p0003_c01] 85 In the name of Apollo beloved of Zeus to whom you, Kalchas, make your prayers when you interpret the gods' will to the Danaans, no man so long as I am alive above earth and see daylight shall lay the weight of his hands on you beside the hollow ships, not one of all the Danaans, even if you mean Agamemnon, 90 who now claims to be far the greatest of all the Achaians.' At this the blameless seer took courage again and spoke forth: 'No, it is not for the sake of some vow or hecatomb he blames u...
```

### Subagent evaluation

**Question:** How does Book 1 show that honour is both personal and political?  
**Expected evidence:** pp. 1–16  
**Expected answer:** Honour begins as personal insult/status injury, but it produces public consequences: Agamemnon dishonours Chryses and Apollo punishes the whole host; Agamemnon dishonours Achilles by taking Briseis; Achilles' anger and withdrawal endanger the army; Thetis and Zeus convert Achilles' grievance into Trojan success and Achaian suffering.

## v2 response assessed

The v2 answer does not actually answer the interpretive question. It returns "Best evidence" snippets from **p. 1** and **p. 3** only:

- p. 1: Agamemnon dishonours Chryses, causing Apollo's plague against the Achaian host.
- p. 3: Kalchas/Achilles scene, including Kalchas' explanation that Apollo blames Agamemnon for dishonouring Chryses and refusing ransom.

Those passages support only the first part of the expected chain: a personal dishonour to Chryses becomes a public plague. The response misses the Achilles/Briseis portion, Achilles' withdrawal, Thetis' appeal to Zeus, and Zeus/Hera's recognition that honouring Achilles means destroying many Achaians.

## Source check

- **p. 1:** Strongly relevant. It says Apollo drove pestilence through the host and people perished because Atreus' son dishonoured Chryses, Apollo's priest.
- **p. 3:** Relevant but redundant with p. 1 for this question. Kalchas explains Apollo blames Agamemnon for dishonouring his priest and refusing to return the daughter or accept ransom.
- **pp. 5–6:** Missing. Achilles frames the war as fought for Agamemnon/Menelaos' honour and says Agamemnon threatens to strip away his own prize; Agamemnon threatens to take Briseis to prove he is greater.
- **pp. 7–8:** Missing in v2. Achilles predicts Achaian losses because Agamemnon did not honour the best Achaian; Nestor links the quarrel to Achaian political/military damage.
- **p. 10:** Missing. Briseis is taken, and Achilles says Agamemnon has dishonoured him.
- **p. 12:** Missing. Achilles asks Thetis to have Zeus help the Trojans and pin the Achaians against the ships until Agamemnon recognizes his dishonour.
- **pp. 14–16:** Missing. Achilles stays out of battle; Thetis asks Zeus to honour Achilles by strengthening the Trojans; Hera interprets Zeus's assent as honouring Achilles and destroying many beside the Achaian ships.

## Rubric scores

| Criterion | Score | Rationale |
|---|---:|---|
| retrieval_relevance | 2/5 | p. 1 and p. 3 are relevant to Chryses/plague, but they cover only one part of a broad pp. 1–16 interpretive chain. The stronger Briseis/Achilles/Thetis/Zeus pages are absent. |
| citation_accuracy | 3/5 | The cited snippets accurately support the claim that dishonouring Chryses caused public plague, but the citation set is too incomplete to support the full answer. |
| speaker_attribution | n/a | The response is essentially evidence-only and makes no substantive speaker/action claims to evaluate. |
| causal_chain | 1/5 | It preserves only the first causal link: dishonour of Chryses → plague. It omits Briseis → Achilles' dishonour/withdrawal → Thetis/Zeus → war-level harm. |
| no_hallucination | 5/5 | No invented claim appears; the failure is omission and non-answer format, not hallucination. |
| answer_quality | 1/5 | It gives evidence excerpts rather than a thesis or explanation of how honour is both personal and political. |

## Diagnosis

- **Retrieval/reranking:** Weak for an abstract, multi-hop question. The system over-concentrates on the lexical cue **"dishonoured"** in the Chryses/Kalchas material and fails to diversify across the later honour vocabulary around **prize**, **Briseis**, **Achilles**, **Thetis**, **Zeus**, **Trojans**, and **Achaians**.
- **Generation:** Primary visible failure. The model outputs a "Best evidence" list instead of synthesizing a direct answer. Even with incomplete retrieval, it could have explained the Chryses/plague political point; it does not.
- **Prompt:** The prompt still appears to permit evidence-dump answers. For this question it should require a short thesis plus 3–4 cited causal steps spanning the whole book.
- **OCR:** Not a meaningful cause. The relevant pages are readable; minor OCR artifacts such as `I0`, `takc`, `Briscis`, `goo`, and `sos` do not explain the missing evidence or lack of synthesis.

## Comparison with v1 / Qwen effect

v1 retrieved **p. 1** and **p. 8**. That was also inadequate and evidence-dump styled, but p. 8 at least gestured toward the political/military dimension through Nestor's comments about Achilles as a bulwark for all Achaians and kingly honour. v2 retrieves **p. 1** and **p. 3**, which are more redundant: both mostly support the Chryses/plague link.

Overall, **Qwen/v2 did not improve Q11 and slightly worsened retrieval coverage**. Generation quality is essentially unchanged: still a non-synthesized evidence list. The main regression is that v2 loses the p. 8 bridge toward army-wide consequences and still misses the decisive Briseis/Thetis/Zeus pages.

## Overall judgment

**Failing/poor.** The result is factually safe but answers only a small fragment of the question. A satisfactory answer needs to connect private honour injuries to public order and military disaster: Chryses' insult causes plague; Briseis' seizure shames Achilles; Achilles withdraws and endangers the army; Thetis and Zeus make Achilles' honour a strategic war-level issue.

## Q12. How does Nestor try to resolve the conflict between Achilles and Agamemnon?

**Test set:** D — Interpretive but source-grounded

### Expected

- Expected evidence: p. 8

- Good answer should mention: Nestor urges restraint; acknowledges Achilles’ strength but Agamemnon’s greater authority; tries to preserve unity among the Achaians.

- Failure signs: Says Nestor takes Achilles’ side completely; says he orders Agamemnon to return Briseis.

### Investigator response \(v2 Ollama/Qwen\)

```md
Question: How does Nestor try to resolve the conflict between Achilles and Agamemnon?
Response: He urges Agamemnon to give up his anger towards Achilles, calling him "a great bulwark of battle." (p.
Evidence:
- [p. 3 | iliad_book1_p0003_c01] 85 In the name of Apollo beloved of Zeus to whom you, Kalchas, make your prayers when you interpret the gods' will to the Danaans, no man so long as I am alive above earth and see daylight shall lay the weight of his hands on you beside the hollow ships, not one of all the Danaans, even if you mean Agamemnon, 90 who now claims to be far the greatest of all the Achaians.' At this the blameless seer took courage again and spoke forth: 'No, it is not for the sake of some vow or hecatomb he blames u...
- [p. 8 | iliad_book1_p0008_c01] Even 280 though you are the stronger man, and the mother who bore you was immortal, yet is this man greater who is lord over more than you rule: Son of Atreus, give up your anger; even I entreat you to give over your bitterness against Achilleus, he who stands as a great bulwark of battle over all the Achaians.' Then in answer again spoke powerful Agamemnon: 285 'Yes, old sir, all this you have said is fair and orderly.
```

### Subagent evaluation

**Question:** How does Nestor try to resolve the conflict between Achilles and Agamemnon?  
**Expected evidence:** p. 8  
**Expected answer:** Nestor tries to calm both men and preserve Achaian unity: he warns that their quarrel helps the Trojans, urges both to heed his counsel, tells Agamemnon not to take Achilles' girl/prize and to give up anger, and tells Achilles not to challenge the greater authority of the sceptred king, even though Achilles is the stronger warrior.

## v2 response assessed

The v2 answer says: "He urges Agamemnon to give up his anger towards Achilles, calling him 'a great bulwark of battle.'" It cites evidence from p. 8, but the displayed citation is malformed/truncated as "(p." and the evidence list also includes an irrelevant p. 3 chunk.

This is partially correct but too narrow. It captures Nestor's final appeal to Agamemnon and the "great bulwark" phrase, but misses the balanced mediation: Nestor speaks "in kind intention toward both," warns that the quarrel will delight Priam and the Trojans, tells Agamemnon not to take Briseis, and tells Achilles not to set himself against Agamemnon's kingly honor and wider rule.

## Source check

- **p. 8:** Nestor says "Great sorrow comes on the land of Achaia" and that Priam, the Trojans, and their allies would rejoice to hear Achilles and Agamemnon quarrelling.
- **p. 8:** He asks both younger men to be persuaded by him.
- **p. 8:** To Agamemnon, he says not to take the girl away, because she was given first as Achilles' prize by the Achaians.
- **p. 8:** To Achilles, he says not to match strength with the king, because Zeus gives the sceptred king a greater portion of honor and Agamemnon rules more men.
- **p. 8:** To Agamemnon again, he asks him to give up anger against Achilles, who is a "great bulwark of battle" for the Achaians.

## Rubric scores

| Criterion | Score | Rationale |
|---|---:|---|
| retrieval_relevance | 4/5 | v2 retrieves the key expected page, p. 8, and the answer-bearing Nestor passage. It loses a point because it also retrieves p. 3, which is unrelated to Nestor's mediation, and the shown p. 8 snippet begins near the end of the speech, omitting earlier unity/compromise material. |
| citation_accuracy | 3/5 | The p. 8 evidence supports the claim that Nestor tells Agamemnon to give up anger and calls Achilles a bulwark. However, the answer citation is malformed as "(p." and the response does not cite the omitted parts of Nestor's strategy. |
| speaker_attribution | 4/5 | The response correctly attributes the advice to Nestor and identifies Agamemnon and Achilles correctly. It is incomplete rather than misattributed. |
| causal_chain | 2/5 | It does not explain why Nestor intervenes or how his advice is meant to resolve the conflict: preventing Achaian division and Trojan advantage through restraint on both sides. |
| no_hallucination | 5/5 | No invented or forbidden claim appears. It does not say Nestor takes Achilles' side completely or orders Agamemnon to return Briseis outright. |
| answer_quality | 3/5 | The answer is direct and mostly grounded, but it is a one-sided summary of Nestor's advice to Agamemnon. It misses the core balanced, conciliatory structure of Nestor's speech. |

## Diagnosis

- **Retrieval/reranking:** Improved substantially over v1 because v2 retrieves p. 8, the required page. Reranking/snippet selection is still imperfect: the top p. 8 snippet emphasizes only the end of Nestor's speech, while p. 3 is irrelevant and should not be surfaced for this question.
- **Generation:** Main remaining weakness. Qwen produces a concise prose answer instead of the old evidence-dump format, but the prose under-synthesizes the evidence and reduces Nestor's balanced mediation to only his appeal to Agamemnon.
- **Prompt:** The prompt likely needs stronger instructions for interpretive questions to cover all relevant cited evidence and identify the speaker's strategy, not just extract a single quotable line.
- **OCR:** Not a meaningful issue. Page 8 is readable, and the needed phrases are clear.

## Comparison with v1

v1 failed this case badly: it retrieved p. 3 and p. 9 but missed p. 8, returned only "Best evidence," and never explained Nestor's role. v2 is clearly better: it finds the crucial page and gives a factually safe partial answer. However, the improvement is incomplete because Qwen/v2 still misses half of Nestor's mediation and includes a malformed citation.

**Overall judgment:** Qwen/v2 improved Q12 from failing to partially successful. It is grounded and non-hallucinatory, but should be scored as only moderate because it omits Nestor's advice to Achilles and the broader unity-preserving purpose of the speech.

## Q13. Find evidence that Agamemnon’s leadership damages the Achaian army.

**Test set:** E — Retrieval difficulty / abstract query

### Expected

- Expected evidence: pp. 1–5, 8–12

- Good answer should mention: His rejection of Chryses brings plague; his demand for compensation creates conflict with Achilles; taking Briseis leads Achilles to withdraw.

- Failure signs: Retrieves only p. 8 or only p. 1; does not connect multiple events.

### Investigator response \(v2 Ollama/Qwen\)

```md
Question: Find evidence that Agamemnon’s leadership damages the Achaian army.
Response: Best evidence:
- [p. 3] 85 In the name of Apollo beloved of Zeus to whom you, Kalchas, make your prayers when you interpret the gods' will to the Danaans, no man so long as I am alive above earth and see daylight shall lay the weight of his hands on you beside the...
- [p. 8] Even 280 though you are the stronger man, and the mother who bore you was immortal, yet is this man greater who is lord over more than you rule: Son of Atreus, give up your anger; even I entreat you to give over your bitterness against Achi...
- [p. 9] But Agamemnon did not give up his anger and the first threat he made to Achilleus, but to Talthybios he gave his orders and Eurybates 320 who were heralds and hard-working henchmen to him: 'Go now to the shelter of Peleus' son Achilleus, to...
Evidence:
- [p. 3 | iliad_book1_p0003_c01] 85 In the name of Apollo beloved of Zeus to whom you, Kalchas, make your prayers when you interpret the gods' will to the Danaans, no man so long as I am alive above earth and see daylight shall lay the weight of his hands on you beside the hollow ships, not one of all the Danaans, even if you mean Agamemnon, 90 who now claims to be far the greatest of all the Achaians.' At this the blameless seer took courage again and spoke forth: 'No, it is not for the sake of some vow or hecatomb he blames u...
- [p. 8 | iliad_book1_p0008_c01] Even 280 though you are the stronger man, and the mother who bore you was immortal, yet is this man greater who is lord over more than you rule: Son of Atreus, give up your anger; even I entreat you to give over your bitterness against Achilleus, he who stands as a great bulwark of battle over all the Achaians.' Then in answer again spoke powerful Agamemnon: 285 'Yes, old sir, all this you have said is fair and orderly.
- [p. 9 | iliad_book1_p0009_c01] But Agamemnon did not give up his anger and the first threat he made to Achilleus, but to Talthybios he gave his orders and Eurybates 320 who were heralds and hard-working henchmen to him: 'Go now to the shelter of Peleus' son Achilleus, to bring back Briseis of the fair cheeks leading her by the hand.
```

### Subagent evaluation

**Question:** Find evidence that Agamemnon’s leadership damages the Achaian army.  
**Expected evidence:** pp. 1–5, 8–12. A strong answer should connect: rejection of Chryses → plague; demand for compensation → quarrel with Achilles; taking Briseis → Achilles withdraws / Achaians suffer.

## Verdict

The v2 result is **partially relevant but inadequate** for an abstract/multi-hop evidence question. It retrieves three useful pages (**p. 3, p. 8, p. 9**) but does not synthesize them into the causal argument requested, and it misses several stronger expected pages, especially **p. 1–2** for the plague and **p. 10–12** for Achilles' withdrawal and his explicit wish that the Achaians be pinned back/dying so Agamemnon recognizes his madness.

## Rubric

| Criterion | Score | Notes |
|---|---:|---|
| retrieval_relevance | 3/5 | p. 3 supports the plague cause; p. 8 has Nestor warning Agamemnon not to take Briseis because Achilles is a bulwark; p. 9 has Agamemnon ordering Briseis taken. But coverage is too narrow for the full chain and misses p. 1–2, p. 4–5, and p. 10–12. |
| citation_accuracy | 4/5 | The cited pages are real and relevant. The p. 3 snippet is truncated before the strongest lines, but the evidence section includes enough to identify Kalchas' explanation. No page mis-citation seen. |
| speaker_attribution | 2/5 | The response does not explain speakers/actions. It leaves the reader to infer that p. 3 includes Achilles/Kalchas, p. 8 is Nestor, and p. 9 is narrator/Agamemnon. |
| causal_chain | 2/5 | It provides fragments, not the chain: Agamemnon dishonors Chryses → Apollo sends plague → Agamemnon demands a replacement prize → threatens/takes Briseis → Achilles withdraws, damaging the army. |
| no_hallucination | 5/5 | No invented or unsupported claims; the failure is omission and lack of synthesis. |
| answer_quality | 2/5 | The answer is still an evidence dump (“Best evidence”) rather than a direct, explanatory answer to the abstract prompt. |

## Source-page check

Important source evidence that v2 should have used or summarized:

- **pp. 1–3:** Agamemnon dishonors Chryses; Apollo sends the plague; Kalchas states Apollo blames them because Agamemnon dishonored the priest and would not return the daughter/accept ransom.
- **pp. 4–5:** Agamemnon says he wants his people safe but immediately demands a replacement prize; Achilles calls him greedy and says he will return home rather than stay dishonored.
- **p. 8:** Nestor warns that the quarrel brings “great sorrow” to Achaia and tells Agamemnon not to take the girl because Achilles is a “great bulwark of battle” for the Achaians.
- **pp. 9–10:** Agamemnon sends heralds to take Briseis; Achilles says Agamemnon lacks foresight and that the Achaians may later need him to beat back destruction.
- **pp. 11–12:** Achilles retells the whole chain and asks Thetis to have Zeus help the Trojans pin the Achaians back, dying, so Agamemnon recognizes his madness.

## Diagnosis

- **Retrieval/reranking:** Partial failure. Retrieval found some relevant mid-chain snippets, but reranking did not ensure event-chain coverage across the required ranges. It omitted the clearest opening plague pages and the later withdrawal/consequence pages.
- **Generation:** Primary failure. The model did not turn retrieved evidence into a concise argument. It merely listed snippets, so the causal claim “Agamemnon’s leadership damages the army” is not explained.
- **Prompt:** Likely needs stronger instructions for abstract evidence questions: cite 2–4 linked events and explicitly state how each event harms the Achaians.
- **OCR:** Not a significant problem. OCR noise exists (`I0`, `I00`, `takc`, `Briscis`), but the relevant passages are readable and adequate.

## v1 comparison / Qwen effect

This v2 Ollama/Qwen result appears **effectively unchanged from v1** for Q13: same key retrieved pages (**p. 3, p. 8, p. 9**) and same evidence-dump style. Qwen did **not meaningfully improve** synthesis, causal chaining, or coverage; it also did not introduce new hallucinations. Overall: **no material improvement, no clear worsening**.

## Q14. Find evidence that divine power responds to human dishonour in Book 1.

**Test set:** E — Retrieval difficulty / abstract query

### Expected

- Expected evidence: pp. 1–3, 12, 14–16

- Good answer should mention: Apollo punishes Agamemnon’s dishonour of Chryses; Achilles/Thetis appeal to Zeus over Achilles’ dishonour.

- Failure signs: Mentions gods vaguely without explaining the human action that triggers divine response.

### Investigator response \(v2 Ollama/Qwen\)

```md
Question: Find evidence that divine power responds to human dishonour in Book 1.
Response: The text on page 3 suggests that divine power responds to human dishonour when it states, "no man so long as I am alive above earth and see daylight shall lay the weight of his hands on you beside the hollow ships, not one of all the Danaans, even if you mean Agamemnon, who now claims to be far the greatest of all the Achaians.' This indicates that Agamemnon's dishonouring of a priest leads to divine retribution.
Evidence:
- [p. 1 | iliad_book1_p0001_c01] ONE BOOK S ING, goddess, the anger of Peleus' son Achilleus and its devastation, which put pains thousandfold upon the Achaians, hurled in their multitudes to the house of Hades strong souls of heroes, but gave their bodies to be the delicate feasting of dogs, of all birds, and the will of Zeus was accomplished 5 since that time when first there stood in division of conflict Atreus' son the lord of men and brilliant Achilleus.
- [p. 3 | iliad_book1_p0003_c01] 85 In the name of Apollo beloved of Zeus to whom you, Kalchas, make your prayers when you interpret the gods' will to the Danaans, no man so long as I am alive above earth and see daylight shall lay the weight of his hands on you beside the hollow ships, not one of all the Danaans, even if you mean Agamemnon, 90 who now claims to be far the greatest of all the Achaians.' At this the blameless seer took courage again and spoke forth: 'No, it is not for the sake of some vow or hecatomb he blames u...
- [p. 8 | iliad_book1_p0008_c01] Even 280 though you are the stronger man, and the mother who bore you was immortal, yet is this man greater who is lord over more than you rule: Son of Atreus, give up your anger; even I entreat you to give over your bitterness against Achilleus, he who stands as a great bulwark of battle over all the Achaians.' Then in answer again spoke powerful Agamemnon: 285 'Yes, old sir, all this you have said is fair and orderly.
```

### Subagent evaluation

**Question:** Find evidence that divine power responds to human dishonour in Book 1.  
**Expected evidence:** pp. 1–3 and 12, 14–16. A good answer should give two chains: (1) Agamemnon dishonours Chryses, so Apollo sends/continues the plague; (2) Agamemnon dishonours Achilles, so Achilles asks Thetis to supplicate Zeus, and Zeus agrees to honour Achilles by helping the Trojans.

## Verdict

V2 is **poor and slightly worse than v1 overall**. It does generate a prose sentence rather than only “Best evidence,” but the sentence is supported by the wrong quoted passage and it still misses the second, crucial Achilles/Thetis/Zeus chain entirely.

## Rubric scores

| Criterion | Score | Notes |
|---|---:|---|
| retrieval_relevance | 2/5 | It retrieves expected pages **p. 1** and **p. 3**, but the displayed snippets are poorly targeted: p. 1 is only the proem/conflict setup, p. 3 is Achilles promising to protect Kalchas, and p. 8 is irrelevant honour/political-status material. It misses pp. 12 and 14–16. |
| citation_accuracy | 1/5 | The answer claims the p. 3 quote shows “Agamemnon’s dishonouring of a priest leads to divine retribution,” but the quoted p. 3 text only shows Achilles protecting Kalchas. The cited evidence does not directly support the generated claim. |
| speaker_attribution | 1/5 | The response does not identify that p. 3 is Achilles speaking to Kalchas, nor Chryses praying to Apollo, nor Thetis supplicating Zeus. |
| causal_chain | 1/5 | It gestures toward one correct chain, Chryses dishonoured → divine retribution, but does not actually cite or explain the human action and divine response. The Achilles dishonoured → Thetis → Zeus chain is absent. |
| no_hallucination | 3/5 | The main generated claim is broadly true in Book 1, but it is not supported by the quoted evidence and over-interprets the p. 3 snippet. No major invented episode appears. |
| answer_quality | 1/5 | The answer is incomplete and misleadingly grounded. It gives one vague example instead of the required thematic synthesis with two episodes and citations. |

## Source check

Relevant source passages are readable in OCR:

- **pp. 1–3:** Apollo sends plague because Atreus’ son dishonoured Chryses, Apollo’s priest. Page 2 has Chryses’ prayer asking Apollo to make the Danaans pay for his tears, and Apollo hears him. Page 3 has Kalchas explicitly saying Apollo blames them because Agamemnon dishonoured his priest and refused ransom.
- **pp. 10–12:** Achilles says Agamemnon has dishonoured him by taking Briseis, then asks Thetis to supplicate Zeus so the Trojans will gain strength and Agamemnon will recognize he “did no honour to the best of the Achaians.”
- **pp. 14–16:** Thetis supplicates Zeus, says Agamemnon dishonoured Achilles, asks Zeus to honour Achilles by strengthening the Trojans, and Zeus nods assent; Hera understands Zeus has agreed to honour Achilles and destroy many Achaeans by the ships.

## Diagnosis

- **Retrieval/reranking:** Main failure. It finds early expected pages nominally but not the best supporting snippets, includes irrelevant p. 8, and completely misses the later Zeus/Thetis evidence.
- **Generation:** Some improvement in format over v1 because v2 attempts a direct sentence. However, it generates a claim from an unsupportive quote and fails to synthesize the two examples requested by the abstract query.
- **Prompt:** The prompt still does not force abstract/theme questions to enumerate multiple episodes with “human dishonour → god appealed/responds → consequence.”
- **OCR:** Not a material issue. The OCR has minor artifacts, but all necessary passages are legible.

## V1 comparison

V1 retrieved stronger Apollo evidence, especially **p. 2** with Chryses praying and Apollo hearing him, though it also included irrelevant p. 8 and missed the Achilles/Thetis/Zeus chain. V2 replaces p. 2 with p. 3 but uses the wrong part of p. 3 in the response. Qwen/v2 therefore **improves surface generation slightly** but **worsens grounding and evidence selection**, and it does not solve the core retrieval/reranking failure for pp. 12 and 14–16.

## Q15. What role does Briseis play in the conflict, beyond being a captured woman?

**Test set:** E — Retrieval difficulty / abstract query

### Expected

- Expected evidence: pp. 6–10, 11–12

- Good answer should mention: Briseis functions as Achilles’ prize and symbol of honour; Agamemnon taking her publicly humiliates Achilles and triggers his withdrawal.

- Failure signs: Reduces Briseis only to romance; gives unsupported character analysis.

### Investigator response \(v2 Ollama/Qwen\)

```md
Question: What role does Briseis play in the conflict, beyond being a captured woman?
Response: This is evident from p.9 where it states, "Agamemnon did not give up his anger and the first threat he made to Achilleus, but to Talthybios he gave his orders and Eurybates... 'Go now to the shelter of Peleus' son Achilleus, to bring back Briseis of the fair cheeks leading her by the hand.'" This action suggests she is used as a pawn in Agamemnon's conflict with Achilles.
Evidence:
- [p. 1 | iliad_book1_p0001_c01] Zeus' son and Leto's, Apollo, who in anger at the king drove the foul pestilence along the host, and the people perished, I0 since Atreus' son had dishonoured Chryses, priest of Apollo, when he came beside the fast ships of the Achaians to ransom back his daughter, carrying gifts beyond count and holding in his hands wound on a staff of gold the ribbons of Apollo who strikes from afar, and supplicated all the Achaians, 15 but above all Atreus' two sons, the marshals of the people: 'Sons of Atreu...
- [p. 9 | iliad_book1_p0009_c01] But Agamemnon did not give up his anger and the first threat he made to Achilleus, but to Talthybios he gave his orders and Eurybates 320 who were heralds and hard-working henchmen to him: 'Go now to the shelter of Peleus' son Achilleus, to bring back Briseis of the fair cheeks leading her by the hand.
- [p. 3 | iliad_book1_p0003_c01] 85 In the name of Apollo beloved of Zeus to whom you, Kalchas, make your prayers when you interpret the gods' will to the Danaans, no man so long as I am alive above earth and see daylight shall lay the weight of his hands on you beside the hollow ships, not one of all the Danaans, even if you mean Agamemnon, 90 who now claims to be far the greatest of all the Achaians.' At this the blameless seer took courage again and spoke forth: 'No, it is not for the sake of some vow or hecatomb he blames u...
```

### Subagent evaluation

**Question:** What role does Briseis play in the conflict, beyond being a captured woman?  
**Expected evidence:** pp. 6–10, 11–12  
**Expected answer:** Briseis is Achilles’ prize/token of honor. Agamemnon’s seizure of her is a public assertion of superiority and a humiliation of Achilles, which helps trigger Achilles’ anger, withdrawal from battle, and appeal through Thetis for Zeus to punish the Achaians.

## Verdict

**Score: weak partial.** v2 gives a direct answer instead of the v1-style evidence dump, but the answer is too thin: calling Briseis a “pawn” does not capture the central honor/prize logic or Achilles’ withdrawal. Retrieval/reranking found one relevant Briseis seizure passage on p. 9, but missed the strongest interpretive support on pp. 5–6 and pp. 10–12.

## Rubric

| Criterion | Score | Notes |
|---|---:|---|
| retrieval_relevance | 2/5 | p. 9 is relevant because Agamemnon orders Briseis taken from Achilles. But p. 1 and p. 3 are background/irrelevant for Briseis’ role, and the result misses key pages: p. 5 prize/honor complaint, p. 6 Agamemnon’s threat to take “your prize,” p. 10 Achilles says Agamemnon dishonored him by taking his prize, and pp. 11–12 link this dishonor to Thetis/Zeus and Achilles’ withdrawal. |
| citation_accuracy | 3/5 | The p. 9 citation accurately supports that Agamemnon has Briseis taken. However, the claim that she is a “pawn” is only an inference from limited evidence, and citations do not substantiate the fuller expected role as honor-token and cause of withdrawal. p. 1 and p. 3 do not support the answer. |
| speaker_attribution | n/a | The answer makes no complex speaker-attribution claims. It correctly names Agamemnon and Achilles in the conflict. |
| causal_chain | 2/5 | It identifies Agamemnon’s action against Achilles, but omits the chain: Briseis = Achilles’ prize/honor → Agamemnon takes her to assert superiority → Achilles is dishonored/humiliated → Achilles withdraws and seeks Zeus’ help through Thetis. |
| no_hallucination | 4/5 | “Pawn” is not directly Homeric wording here, but it is a reasonable compressed interpretation. No romance/unsupported personality analysis appears. |
| answer_quality | 2/5 | Better than v1 because it attempts a synthesized answer, but it is one-dimensional and under-supported. It would not satisfy the abstract question’s main target: Briseis as the symbolic prize of honor whose seizure causes Achilles’ rupture with Agamemnon. |

## Source check

Relevant source passages not retrieved or not used:

- **p. 5:** Achilles frames the dispute in terms of labor, distribution of booty, and honor: Agamemnon threatens to strip away “my prize,” the “gift of the sons of the Achaians,” leaving Achilles to stay “dishonoured.”
- **p. 6:** Agamemnon explicitly threatens to take “the fair-cheeked Briseis, your prize,” so Achilles learns “how much greater I am than you.” This is the clearest evidence that Briseis functions as a status/honor token.
- **p. 10:** Achilles lets the heralds take Briseis but says Agamemnon “has dishonoured me, since he has taken away my prize and keeps it.”
- **pp. 11–12:** Achilles recounts the completed threat to Thetis and asks her to supplicate Zeus so the Achaians suffer until Agamemnon recognizes he “did no honour to the best of the Achaians.” Thetis tells Achilles to stay by the ships and away from fighting.

## Diagnosis

- **Retrieval/reranking:** Main weakness. The system retrieved one direct Briseis seizure chunk but failed to retrieve/rank the honor-prize passages that answer “beyond being a captured woman.” It appears to overvalue direct name matches and generic Agamemnon/Achilles/“dishonoured” background while missing semantically crucial terms like `prize`, `honour`, `gift`, `outrage`, and `stay away from fighting`.
- **Generation:** Improved over v1 by producing an actual sentence answer. Still weak because it does not synthesize the broader evidence into the expected honor/withdrawal explanation.
- **Prompt:** The prompt likely now encourages answer formation, but it still needs stronger requirements to answer abstract questions with a causal interpretation and cite the best supporting passages.
- **OCR:** Minor contributing issue only. p. 6 has OCR noise (`takc`, `angcr`, `Briscis`, `hcrc`), which could hurt lexical retrieval for “Briseis”/“take”/“anger,” but the relevant text remains readable. OCR is not the primary failure.

## v1 comparison / Qwen effect

v1 retrieved p. 9 and p. 10 plus irrelevant p. 1, but gave no synthesized answer. v2 **improves generation** by giving a direct answer and avoiding the evidence-only format. However, v2 **worsens retrieval coverage** slightly by losing p. 10 and still missing pp. 5–6 and 11–12. Overall, Qwen/v2 is a modest improvement in answer format but not in substantive correctness; the final answer remains underdeveloped and under-evidenced.

## Q16. Write a 300-word answer: How does Book 1 present the relationship between anger, honour, and military disaster?

**Test set:** F — Essay-style RAG stress tests

### Expected

- Expected evidence: pp. 1–16

- Good answer should mention: Opening invocation, Apollo’s plague, Achilles/Agamemnon quarrel, Briseis, Thetis/Zeus.

- Failure signs: Over-focuses on one scene; weak citations; no chain of causality.

### Investigator response \(v2 Ollama/Qwen\)

```md
Question: Write a 300-word answer: How does Book 1 present the relationship between anger, honour, and military disaster?
Response: Best evidence:
- [p. 8] Even 280 though you are the stronger man, and the mother who bore you was immortal, yet is this man greater who is lord over more than you rule: Son of Atreus, give up your anger; even I entreat you to give over your bitterness against Achi...
- [p. 9] But Agamemnon did not give up his anger and the first threat he made to Achilleus, but to Talthybios he gave his orders and Eurybates 320 who were heralds and hard-working henchmen to him: 'Go now to the shelter of Peleus' son Achilleus, to...
Evidence:
- [p. 8 | iliad_book1_p0008_c01] Even 280 though you are the stronger man, and the mother who bore you was immortal, yet is this man greater who is lord over more than you rule: Son of Atreus, give up your anger; even I entreat you to give over your bitterness against Achilleus, he who stands as a great bulwark of battle over all the Achaians.' Then in answer again spoke powerful Agamemnon: 285 'Yes, old sir, all this you have said is fair and orderly.
- [p. 9 | iliad_book1_p0009_c01] But Agamemnon did not give up his anger and the first threat he made to Achilleus, but to Talthybios he gave his orders and Eurybates 320 who were heralds and hard-working henchmen to him: 'Go now to the shelter of Peleus' son Achilleus, to bring back Briseis of the fair cheeks leading her by the hand.
```

### Subagent evaluation

**Question:** Write a 300-word answer: How does Book 1 present the relationship between anger, honour, and military disaster?  
**Expected evidence:** pp. 1–16  
**Expected answer:** A synthesis linking the opening invocation, Apollo’s plague, Achilles/Agamemnon quarrel, Briseis as prize/honor token, Achilles’ withdrawal, and Thetis/Zeus arranging future Achaian losses.

## Verdict

**Score: poor / non-answer.** v2 does not write a 300-word answer. It returns only “Best evidence” bullets and two source excerpts. The two passages are relevant pieces of the theme—Nestor warning Agamemnon to give up anger because Achilles is a battle bulwark, and Agamemnon refusing to give up anger before ordering Briseis seized—but they are far too narrow for a Book-wide essay and do not establish the required causal chain.

## Rubric

| Criterion | Score | Notes |
|---|---:|---|
| retrieval_relevance | 2/5 | p. 8 and p. 9 are relevant to anger, honor hierarchy, and Briseis. But the result misses the opening invocation and Apollo’s plague on pp. 1–3, Achilles’ honor complaint and withdrawal on pp. 10–12, and Thetis/Zeus on pp. 14–15. |
| citation_accuracy | 4/5 | The cited passages are accurately quoted and support limited claims about Agamemnon’s anger and the Briseis seizure. They cannot support the full essay because most required evidence is absent. |
| speaker_attribution | n/a | There is no substantive prose answer to assess. The p. 8 passage is Nestor’s speech, but the response does not identify him. |
| causal_chain | 1/5 | It gestures at anger and Briseis but does not connect dishonor → divine plague → quarrel over prizes → Achilles’ withdrawal → Thetis’ appeal to Zeus → military disaster. |
| no_hallucination | 5/5 | No invented claims; the failure is omission and lack of synthesis. |
| answer_quality | 0/5 | It ignores the requested 300-word essay format and gives evidence only. |

## Source check

Important available source material not retrieved/used:

- **p. 1:** The poem opens with Achilles’ anger and its “devastation,” “pains thousandfold,” and the will of Zeus; Apollo’s anger follows Agamemnon’s dishonoring of Chryses.
- **pp. 2–3:** Chryses’ prayer and Kalchas’ explanation make the first military disaster a direct result of dishonor and divine anger.
- **pp. 5–6:** Achilles frames Agamemnon’s behavior as unequal reward and dishonor; Agamemnon threatens to take “the fair-cheeked Briseis, your prize” to show superiority.
- **pp. 10–12:** Briseis is actually taken; Achilles says Agamemnon has dishonored him by taking his prize, asks Thetis to supplicate Zeus, and wants the Achaians pinned back and dying until Agamemnon recognizes he did no honor to the best Achaian.
- **pp. 14–15:** Achilles remains away from assemblies and battle; Thetis asks Zeus to honor Achilles by strengthening the Trojans, and Zeus assents, setting up future Achaian disaster.

## Diagnosis

- **Generation:** Primary failure. Despite an essay prompt, v2 produced the same evidence-list format seen in many v1 outputs, not a synthesized answer.
- **Retrieval/reranking:** Also weak. For a broad essay question, retrieval should diversify across the beginning, quarrel, Briseis/withdrawal, and Zeus/Thetis endpoint. Instead it over-concentrates on adjacent quarrel pages (pp. 8–9).
- **Prompt:** The answer prompt still needs a hard requirement to compose prose when asked for an essay, use multiple citations, and cover the full causal arc rather than merely list top snippets.
- **OCR:** Not a major blocker. Relevant passages are readable. Minor OCR noise exists elsewhere (`I0`, `takc`, `Briscis`, `goo`), but it does not explain the evidence-only response.

## v1 comparison / Qwen effect

v1 also failed generation by returning evidence only. Its retrieval had **p. 1 + p. 8**, which at least included the opening invocation/plague frame and Nestor’s warning, but missed Briseis and Thetis/Zeus. v2 has **p. 8 + p. 9**, gaining a direct Briseis-seizure passage but losing the crucial opening invocation/Apollo plague evidence. Overall, Qwen/v2 **did not improve generation** for this essay case and **slightly worsened thematic coverage**: it is still a non-answer and no longer includes the Book’s opening causal frame.

## Q17. Write a 500-word answer: In Book 1, how do priests, prophets, warriors, kings, and gods each shape the conflict?

**Test set:** F — Essay-style RAG stress tests

### Expected

- Expected evidence: pp. 1–16

- Good answer should mention: Chryses, Kalchas, Achilles, Agamemnon, Thetis, Zeus, Hera.

- Failure signs: Omits Chryses/Kalchas; confuses speakers; cites loosely.

### Investigator response \(v2 Ollama/Qwen\)

```md
Question: Write a 500-word answer: In Book 1, how do priests, prophets, warriors, kings, and gods each shape the conflict?
Response: Best evidence:
- [p. 8] Even 280 though you are the stronger man, and the mother who bore you was immortal, yet is this man greater who is lord over more than you rule: Son of Atreus, give up your anger; even I entreat you to give over your bitterness against Achi...
- [p. 3] 85 In the name of Apollo beloved of Zeus to whom you, Kalchas, make your prayers when you interpret the gods' will to the Danaans, no man so long as I am alive above earth and see daylight shall lay the weight of his hands on you beside the...
Evidence:
- [p. 8 | iliad_book1_p0008_c01] Even 280 though you are the stronger man, and the mother who bore you was immortal, yet is this man greater who is lord over more than you rule: Son of Atreus, give up your anger; even I entreat you to give over your bitterness against Achilleus, he who stands as a great bulwark of battle over all the Achaians.' Then in answer again spoke powerful Agamemnon: 285 'Yes, old sir, all this you have said is fair and orderly.
- [p. 3 | iliad_book1_p0003_c01] 85 In the name of Apollo beloved of Zeus to whom you, Kalchas, make your prayers when you interpret the gods' will to the Danaans, no man so long as I am alive above earth and see daylight shall lay the weight of his hands on you beside the hollow ships, not one of all the Danaans, even if you mean Agamemnon, 90 who now claims to be far the greatest of all the Achaians.' At this the blameless seer took courage again and spoke forth: 'No, it is not for the sake of some vow or hecatomb he blames u...
```

### Subagent evaluation

**Question:** Write a 500-word answer: In Book 1, how do priests, prophets, warriors, kings, and gods each shape the conflict?  
**Expected evidence:** pp. 1–16  
**Expected answer:** A synthesized essay mentioning Chryses, Kalchas, Achilles, Agamemnon, Thetis, Zeus, and Hera, explaining how priestly supplication, prophetic truth-telling, warrior honor, royal authority, and divine politics all escalate the conflict.

## Verdict

**Score: poor / non-answer.** v2 does not write the requested 500-word answer. It returns a “Best evidence” list with only two snippets, from p. 8 and p. 3. Those snippets are not fabricated and one of them usefully covers Kalchas, Achilles, and Agamemnon, but the result gives no essay synthesis and omits most required actors: Chryses as named priest, Thetis, Zeus, and Hera as agents in the divine part of the conflict.

## Rubric

| Criterion | Score | Notes |
|---|---:|---|
| retrieval_relevance | 2/5 | p. 3 is relevant for Kalchas as prophet and Achilles’ promise to protect him from Agamemnon. p. 8 is relevant to the Achilles/Agamemnon hierarchy dispute via Nestor’s mediation, but it is not enough for the full essay. Retrieval misses essential pages: pp. 1–2 for Chryses and Apollo’s plague; pp. 4–10 for Agamemnon’s compensation demand and Briseis; pp. 10–12 and 14–16 for Thetis, Zeus, and Hera. |
| citation_accuracy | 3/5 | The cited snippets accurately come from the pages listed and support narrow points about Kalchas/Achilles/Agamemnon and Nestor’s warning. But the citations cannot support the requested broad answer because key categories and figures are absent. |
| speaker_attribution | n/a | There is no generated essay with substantive speaker claims to assess. The evidence snippet itself preserves speakers reasonably, but the system makes almost no claims. |
| causal_chain | 1/5 | It gives isolated middle-chain evidence only. It does not connect Chryses’ supplication → Apollo’s plague → Kalchas’ revelation → Agamemnon’s royal demand → Achilles’ dishonor/withdrawal → Thetis’ appeal → Zeus’ nod → Hera’s suspicion. |
| no_hallucination | 5/5 | No invented content is visible; the failure is omission and non-generation rather than hallucination. |
| answer_quality | 0/5 | It is not 500 words, not an essay, and does not answer how each social/divine role shapes the conflict. |

## Source check

Relevant support available in the OCR but not retrieved/used:

- **Priests / Chryses (pp. 1–2, 11, 13):** Chryses, Apollo’s priest, comes with ransom for his daughter; Agamemnon rejects him; Chryses prays to Apollo, who sends the plague. Later Odysseus returns Chryseis and Chryses prays for the plague to end.
- **Prophets / Kalchas (p. 3):** Kalchas is “far the best of the bird interpreters,” fears angering the king, and reveals that Apollo is punishing the Achaians because Agamemnon dishonored Chryses.
- **Warriors / Achilles (pp. 2–7, 9–12, 14):** Achilles calls the assembly, protects Kalchas, challenges Agamemnon, nearly draws his sword, gives up Briseis under protest, withdraws from fighting, and asks Thetis to seek Zeus’ help against the Achaians.
- **Kings / Agamemnon (pp. 1–10):** Agamemnon’s royal power drives the crisis: he refuses Chryses, insults Kalchas, demands compensation, and takes Briseis to assert superiority over Achilles.
- **Gods / Thetis, Zeus, Hera (pp. 10–16):** Thetis agrees to supplicate Zeus; Zeus nods to honor Achilles by strengthening the Trojans; Hera suspects the plan and quarrels with Zeus, extending the mortal conflict into Olympus.

## Diagnosis

- **Retrieval/reranking:** Under-diverse and poorly matched to essay scope. v2 retrieved two middle-conflict snippets but did not cover the required beginning, escalation, and Olympian ending. For broad essay questions, reranking should optimize actor/event coverage, not just local lexical relevance.
- **Generation:** Main failure. The answer model did not synthesize the evidence into prose and did not obey the requested 500-word format. The output looks like a fallback evidence-only response.
- **Prompt:** The prompt likely still permits “best evidence” output even when the user asks for an essay. It needs explicit essay-mode requirements: include required figures, organize by role category, and cite each paragraph from multiple page ranges.
- **OCR:** Not a major cause. There are minor OCR artifacts in Book 1 (`I0`, `goo`, `sos`, `takc`, `Briscis`), but the crucial names and plot details are readable enough.

## v1 comparison / Qwen effect

v1 also failed generation, returning only evidence rather than an essay, but it retrieved p. 1 and p. 15: weak anchors for the opening cause and the Thetis/Zeus endpoint. v2 retrieves p. 3 and p. 8 instead, improving coverage of **Kalchas** and the Achilles/Agamemnon hierarchy dispute, but losing the stronger **Chryses/Apollo** opening and the **Thetis/Zeus/Hera** divine ending. Overall, Qwen/v2 does **not** improve Q17 materially; it changes the evidence mix and arguably worsens broad coverage while still failing the core essay-generation requirement.

## Q18. Write a 500-word answer: Is Agamemnon’s authority portrayed as legitimate, abusive, or both in Book 1?

**Test set:** F — Essay-style RAG stress tests

### Expected

- Expected evidence: pp. 1–10

- Good answer should mention: He is king/commander, but rejects Chryses harshly, attacks Kalchas, demands compensation, and takes Briseis.

- Failure signs: Gives a one-sided answer with no evidence for rank/authority.

### Investigator response \(v2 Ollama/Qwen\)

```md
Question: Write a 500-word answer: Is Agamemnon’s authority portrayed as legitimate, abusive, or both in Book 1?
Response: Best evidence:
- [p. 8] Even 280 though you are the stronger man, and the mother who bore you was immortal, yet is this man greater who is lord over more than you rule: Son of Atreus, give up your anger; even I entreat you to give over your bitterness against Achi...
- [p. 1] ONE BOOK S ING, goddess, the anger of Peleus' son Achilleus and its devastation, which put pains thousandfold upon the Achaians, hurled in their multitudes to the house of Hades strong souls of heroes, but gave their bodies to be the delica...
- [p. 3] 85 In the name of Apollo beloved of Zeus to whom you, Kalchas, make your prayers when you interpret the gods' will to the Danaans, no man so long as I am alive above earth and see daylight shall lay the weight of his hands on you beside the...
Evidence:
- [p. 8 | iliad_book1_p0008_c01] Even 280 though you are the stronger man, and the mother who bore you was immortal, yet is this man greater who is lord over more than you rule: Son of Atreus, give up your anger; even I entreat you to give over your bitterness against Achilleus, he who stands as a great bulwark of battle over all the Achaians.' Then in answer again spoke powerful Agamemnon: 285 'Yes, old sir, all this you have said is fair and orderly.
- [p. 1 | iliad_book1_p0001_c01] ONE BOOK S ING, goddess, the anger of Peleus' son Achilleus and its devastation, which put pains thousandfold upon the Achaians, hurled in their multitudes to the house of Hades strong souls of heroes, but gave their bodies to be the delicate feasting of dogs, of all birds, and the will of Zeus was accomplished 5 since that time when first there stood in division of conflict Atreus' son the lord of men and brilliant Achilleus.
- [p. 3 | iliad_book1_p0003_c01] 85 In the name of Apollo beloved of Zeus to whom you, Kalchas, make your prayers when you interpret the gods' will to the Danaans, no man so long as I am alive above earth and see daylight shall lay the weight of his hands on you beside the hollow ships, not one of all the Danaans, even if you mean Agamemnon, 90 who now claims to be far the greatest of all the Achaians.' At this the blameless seer took courage again and spoke forth: 'No, it is not for the sake of some vow or hecatomb he blames u...
```

### Subagent evaluation

**Question:** Write a 500-word answer: Is Agamemnon’s authority portrayed as legitimate, abusive, or both in Book 1?  
**Expected evidence:** pp. 1–10  
**Expected answer:** Both. Agamemnon has real institutional rank as king/commander, but Book 1 shows him using that authority abusively: he rejects Chryses harshly, attacks Kalchas, demands compensation, threatens to take Briseis, and has Briseis removed from Achilles.

## Verdict

**Score: poor / failed essay answer.** v2 retrieves some relevant authority evidence, especially Agamemnon as “lord of men,” Kalchas’ fear of the man with “great kingship,” and Nestor’s statement that Agamemnon is “lord over more.” But the response is still only a “Best evidence” list, not a 500-word interpretive answer. It is also badly unbalanced: it supports the legitimacy/rank side much better than the abuse side and misses most of the required abuse evidence.

## Rubric

| Criterion | Score | Notes |
|---|---:|---|
| retrieval_relevance | 3/5 | All retrieved pages are in the expected pp. 1–10 range and relevant to authority/rank, but the result misses central abuse passages on pp. 2, 4, 6, and 10. |
| citation_accuracy | 4/5 | The quoted snippets are accurately paged and support Agamemnon’s status/authority. They do not support the full balanced answer because the strongest abuse evidence is absent. |
| speaker_attribution | 2/5 | The evidence includes speech contexts, but the response does not identify who is speaking or analyze Nestor/Kalchas/Achilles’ perspectives. |
| causal_chain | 1/5 | The answer does not explain the Book 1 chain: Chryses rejected → Apollo’s plague → Kalchas’ accusation → Agamemnon’s anger/compensation demand → threat and seizure of Briseis → Achilles’ withdrawal. |
| no_hallucination | 5/5 | No invented claim appears; the failure is omission and non-synthesis, not hallucination. |
| answer_quality | 1/5 | It does not produce the requested 500-word answer and does not directly answer “legitimate, abusive, or both.” |

## Source check

Relevant passages in the expected range:

- **p. 1:** Agamemnon is introduced as “Atreus’ son the lord of men,” and Chryses supplicates the Achaians and especially “Atreus’ two sons, the marshals of the people.” This supports legitimate public rank.
- **p. 2:** Agamemnon “harshly” drives Chryses away, refuses to return the girl, and threatens him. This is key abuse evidence and was not retrieved.
- **p. 3:** Kalchas fears a man who “holds great kingship over the men of Argos, and all the Achaians obey him.” This supports Agamemnon’s real authority.
- **p. 4:** Agamemnon attacks Kalchas as a “seer of evil,” admits he refused ransom for Chryseis, and demands another prize so he will not go without. This key abuse/greed passage was not retrieved.
- **p. 6:** Agamemnon threatens to take “the fair-cheeked Briseis, your prize” so Achilles will learn “how much greater I am than you.” This is one of the clearest examples of abusive authority and was not retrieved.
- **p. 8:** Nestor says Agamemnon, as “sceptred king,” has a greater portion of honor from Zeus and is “lord over more”; he also tells Agamemnon not to take the girl. v2 retrieved this, but only the rank side is usable without synthesis.
- **p. 10:** Agamemnon’s heralds take Briseis; Achilles calls him a “cruel king” and says he lacks the sense to protect the Achaians. This completed abuse evidence was not retrieved.

## Diagnosis

- **Retrieval/reranking:** Partial but unbalanced. Reranking appears to favor explicit rank/authority language (`lord`, `great kingship`, `sceptred king`, `greater`) over event coverage. For this essay question, retrieval needed at least one citation for legitimate authority and several for abusive exercise of authority.
- **Generation:** Major failure. The model returned evidence bullets instead of the requested essay, with no thesis, no paragraph structure, and no conclusion that Agamemnon is portrayed as both legitimate and abusive.
- **Prompt:** Still too evidence-list oriented for essay-style questions. It should require a direct thesis first, then integrated citations.
- **OCR:** Minor only. OCR noise exists elsewhere in the relevant passages, especially p. 6 (`takc`, `angcr`, `Briscis`), which may hurt lexical retrieval, but the text is readable enough and OCR is not the main cause.

## v1 comparison / Qwen effect

v1 for Q18 produced essentially the same evidence-only output: pp. 8, 1, and 3, with no synthesized 500-word answer and no key abuse passages. v2/Qwen therefore shows **no meaningful improvement** on this case. It is not clearly worse, but it fails in the same ways: evidence-only generation, rank-side retrieval bias, and missing the Chryses/Kalchas/Briseis abuse sequence.
