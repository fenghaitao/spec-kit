# latest-windsurf Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-10-26

## Active Technologies
- DML 1.4 + Simics Base 7.57.0, utility.dml, simics/devs/signal.dml, simics/device-api.dml (001-read-the-simics)

## Project Structure
```
simics-project/
└── modules/device-name/
    ├── device-name.dml
    ├── registers.dml
    ├── interfaces.dml
    ├── sub-feature.dml
    ├── module_load.py
    ├── CMakeLists.txt
    └── test/
        ├── CMakeLists.txt
        ├── SUITEINFO
        ├── s-device-name.py
        ├── test_name_common.py
        └── README
```

## Commands
# Add commands for DML 1.4

## Code Style
DML 1.4: Follow standard conventions

## Recent Changes
- 001-read-the-simics: Added DML 1.4 + Simics Base 7.57.0, utility.dml, simics/devs/signal.dml, simics/device-api.dml

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->