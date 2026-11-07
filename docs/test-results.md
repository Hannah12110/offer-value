# Repository validation

Executed 2026-11-07 with Python 3.13.4.

67 tests passed; dependency-free package validation passed. Codex host auto-discovery and Python 3.10 were not separately tested. The official quick_validate tool was unavailable in the development environment because PyYAML was absent.

```text
tests: PASS
test_fake_iso_rejected (test_compensation.Compensation.test_fake_iso_rejected) ... ok
test_foreign_no_chinese_tax (test_compensation.Compensation.test_foreign_no_chinese_tax) ... ok
test_generic_foreign (test_compensation.Compensation.test_generic_foreign) ... ok
test_invalid_values (test_compensation.Compensation.test_invalid_values) ... ok
test_mixed_currency (test_compensation.Compensation.test_mixed_currency) ... ok
test_override_above_gross (test_compensation.Compensation.test_override_above_gross) ... ok
test_separation (test_compensation.Compensation.test_separation) ... ok
test_tax_boundaries (test_compensation.Compensation.test_tax_boundaries) ... ok
test_tax_savings (test_compensation.Compensation.test_tax_savings) ... ok
test_unknown (test_compensation.Compensation.test_unknown) ... ok
test_unknown_allowance_keeps_known_floor (test_compensation.Compensation.test_unknown_allowance_keeps_known_floor) ... ok
test_unknown_bonus (test_compensation.Compensation.test_unknown_bonus) ... ok
test_unknown_contributions (test_compensation.Compensation.test_unknown_contributions) ... ok
test_unverified_policy (test_compensation.Compensation.test_unverified_policy) ... ok
test_zero_unknown_distinct (test_compensation.Compensation.test_zero_unknown_distinct) ... ok
test_bad_date (test_evidence.Evidence.test_bad_date) ... ok
test_company_self_report (test_evidence.Evidence.test_company_self_report) ... ok
test_conflict_dangling (test_evidence.Evidence.test_conflict_dangling) ... ok
test_duplicates (test_evidence.Evidence.test_duplicates) ... ok
test_enum_wrong_type (test_evidence.Evidence.test_enum_wrong_type) ... ok
test_estimate (test_evidence.Evidence.test_estimate) ... ok
test_missing_url (test_evidence.Evidence.test_missing_url) ... ok
test_private (test_evidence.Evidence.test_private) ... ok
test_stale (test_evidence.Evidence.test_stale) ... ok
test_user_goal (test_evidence.Evidence.test_user_goal) ... ok
test_valid (test_evidence.Evidence.test_valid) ... ok
test_anonymous_not_covered (test_scoring.Scoring.test_anonymous_not_covered) ... ok
test_bad_top_level (test_scoring.Scoring.test_bad_top_level) ... ok
test_compare_currency (test_scoring.Scoring.test_compare_currency) ... ok
test_compare_dominance (test_scoring.Scoring.test_compare_dominance) ... ok
test_compare_mismatch (test_scoring.Scoring.test_compare_mismatch) ... ok
test_compare_overlap (test_scoring.Scoring.test_compare_overlap) ... ok
test_comparison_cutoff_mismatch (test_scoring.Scoring.test_comparison_cutoff_mismatch) ... ok
test_comparison_cutoff_required (test_scoring.Scoring.test_comparison_cutoff_required) ... ok
test_complete (test_scoring.Scoring.test_complete) ... ok
test_conflict (test_scoring.Scoring.test_conflict) ... ok
test_dangling (test_scoring.Scoring.test_dangling) ... ok
test_empty (test_scoring.Scoring.test_empty) ... ok
test_empty_currency_rejected (test_scoring.Scoring.test_empty_currency_rejected) ... ok
test_endpoint_changes_decision (test_scoring.Scoring.test_endpoint_changes_decision) ... ok
test_failure_keeps_denominator (test_scoring.Scoring.test_failure_keeps_denominator) ... ok
test_goal_cannot_clear_employer_blockers (test_scoring.Scoring.test_goal_cannot_clear_employer_blockers) ... ok
test_goal_conflict (test_scoring.Scoring.test_goal_conflict) ... ok
test_hard_blocker_precedence (test_scoring.Scoring.test_hard_blocker_precedence) ... ok
test_interval (test_scoring.Scoring.test_interval) ... ok
test_missing_blocker_evidence (test_scoring.Scoring.test_missing_blocker_evidence) ... ok
test_missing_salary_flag_even_full_scores (test_scoring.Scoring.test_missing_salary_flag_even_full_scores) ... ok
test_nan_bool_negative (test_scoring.Scoring.test_nan_bool_negative) ... ok
test_no_salary (test_scoring.Scoring.test_no_salary) ... ok
test_omitted_indicator_rejected (test_scoring.Scoring.test_omitted_indicator_rejected) ... ok
test_one_way_conflict_excludes_both (test_scoring.Scoring.test_one_way_conflict_excludes_both) ... ok
test_sensitivity (test_scoring.Scoring.test_sensitivity) ... ok
test_unknown_c_mode (test_scoring.Scoring.test_unknown_c_mode) ... ok
test_unrelated_public_fact_cannot_clear (test_scoring.Scoring.test_unrelated_public_fact_cannot_clear) ... ok
test_unverified_blocker_cannot_clear (test_scoring.Scoring.test_unverified_blocker_cannot_clear) ... ok
test_verbal (test_scoring.Scoring.test_verbal) ... ok
test_verbal_consistent_at_seventy (test_scoring.Scoring.test_verbal_consistent_at_seventy) ... ok
test_weight_sum (test_scoring.Scoring.test_weight_sum) ... ok
test_wrong_dimension_not_covered (test_scoring.Scoring.test_wrong_dimension_not_covered) ... ok
test_calculators_cli (test_workflow.Workflow.test_calculators_cli) ... ok
test_cli_end_to_end_no_overwrite (test_workflow.Workflow.test_cli_end_to_end_no_overwrite) ... ok
test_different_city_no_default_profile (test_workflow.Workflow.test_different_city_no_default_profile) ... ok
test_minimum_offline (test_workflow.Workflow.test_minimum_offline) ... ok
test_missing_city (test_workflow.Workflow.test_missing_city) ... ok
test_no_upload_client_in_scripts (test_workflow.Workflow.test_no_upload_client_in_scripts) ... ok
test_package_static (test_workflow.Workflow.test_package_static) ... ok
test_partial_sections_not_fabricated (test_workflow.Workflow.test_partial_sections_not_fabricated) ... ok

----------------------------------------------------------------------
Ran 67 tests in 0.376s

OK

structure: PASS
{
  "valid": true,
  "errors": [],
  "scope": "restricted YAML scalars, local links, JSON, Python syntax; not Codex runtime discovery"
}

```
