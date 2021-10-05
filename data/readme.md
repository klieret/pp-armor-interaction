**NOTE**: Always edit the yaml file if present and convert it to json with

```bash
python3 -c 'import sys, yaml, json; json.dump(yaml.load(sys.stdin), sys.stdout, indent=4)' < file.yaml > file.json
```

Reason that we don't use yaml files: it's not part of the standard library
so brython doesn't understand it.
