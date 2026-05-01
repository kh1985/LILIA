# Autosave Tick Check

1. Run `./lilia scene-tick test_profile_scene_002`.
2. Confirm `saves/test_profile_scene_002/session.json` has a larger `autosave.turns_since_save`.
3. Run `./lilia scene-tick test_profile_scene_002` until the 10th tick after save.
4. Confirm `autosave.autosave_required` becomes `true`.
5. Run `./lilia apply-turn test_profile_scene_002 tests/apply_turn/sample_turn_update.md`.
6. Confirm `autosave.turns_since_save` returns to `0` and `autosave.autosave_required` returns to `false`.

`scene-tick` is not Save Mode and does not update profile, memory, relationship, or hotset. It only records that a normal play turn has passed and signals when a save is recommended.
