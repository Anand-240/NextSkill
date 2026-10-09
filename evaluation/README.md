# Evidence kits (pending until a person fills them)

Neither file below contains labels or participant data written by this repository.

## Hand labels: labels_template.csv

20 eligible listings drawn at random (seed 20261009) from the six saved markets collected after the matcher rules
were written (Hyderabad, Pune and Jaipur data analyst; Indore data analyst; Jaipur accountant; Dehradun
digital marketing). Pool: 70 eligible listings. The Bengaluru and Noida demos and the validation fixtures were used
while writing the rules, so they are excluded. Regenerate with `python -m scripts.make_label_template`.

For each row read `description_text` yourself and fill, without looking at NextSkill's output:

- `skills_required`: skills the listing asks for, separated by semicolons (example `SQL; Excel`), or `none`
- `skills_mandatory`: only skills stated as must, mandatory, required, essential or minimum, or `none`
- `min_years_experience`: whole number of years the candidate needs; `0` when no minimum is stated

Then run `python -m scripts.score_labels`. It writes reports/hand_label_eval.md. A row counts only when all three
label cells are filled.

## User test: user_test_template.csv

One row per real participant. `unaided_choice` is what they would learn next before seeing NextSkill,
`nextskill_choice` is what they would learn after, `changed_choice` is yes or no, `trust_1_to_5` is a whole number.
Only add a quote with `quote_permission` set to yes. Run `python -m scripts.summarise_user_test` to write
reports/user_test.md. Empty files produce a "pending" report.
