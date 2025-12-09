# Sound Ninja

This filter is used to automatically add a sound reference to every blocks of `BP/blocks`.
Simply add a `sound` field into the description of a file:

```jsonc
{
  "format_version": "1.21.120",
  "minecraft:block": {
    "description": {
      "identifier": "glmn:block_1",
      "sound": "sound_1",
      "menu_category": ...
    },
    // rest of file
  }
}
```




This will add a key in `RP/blocks.json` such as: 

```json
{
  "glmn:block_1": {
    "sound": "sound_1"
  }
}
```