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



## How to install ?
simply run in your regolith folder:
`regolith install github.com/Golimane/sound_ninja`
then add it to your profile


## How to use ?
After installing it, call the filter in your profile
```jsonc
{
  "profiles": {
    "default": {
      "filters": [
        {
          "filter": "sound_ninja",
          "settings": {
            // see bellow
          }
        }
      ]
    }
  }
}
```

## Settings
You can add multiple settings in the filter:
  - `behaviorPack`: path to the build behavior pack, default is set to `./BP` 
  - `resourcePack`: path to the build resource pack, default is set to `./RP`
  - `formatVersion`: if the filde `[RP]/blocks.json` is not specified, the filter will create one with this format_version, default set to "1.21.40"
  - `forceSound`: (On work) when set, will force block with no sound definition to this value


## Changelog
  # 1.0.0
    - First public version of the filter