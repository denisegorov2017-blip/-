# Automatic Test Data Cleanup and Subfolder Organization

## Overview

The automatic test data cleanup and subfolder organization system is designed to improve the structure of the project's results directory. This system automatically:

1. Organizes existing files into appropriate subfolders based on their type
2. Cleans up old test data to save space
3. Removes empty directories to maintain a clean file structure
4. Provides statistics on test and real data

## Directory Structure

After applying the system, all data in the `results` directory will be organized as follows:

```
results/
├── тестовые_данные/          # All test data
└── реальные_данные/          # All real data
```

Empty directories are automatically removed to maintain a clean structure.

## File Classification

Files are classified according to the following rules:

### Test Data
Files that contain the following keywords in their name:
- `test` (any case)
- `тест`
- `fish_batch_test_results`
- `оптимизация`
- And other similar patterns

### Real Data
Files that contain the following keywords in their name:
- `b3ded820-4385-4a42-abc7-75dc0756d335` (unique identifier for real data)
- `вся номенклатура`

### Undefined Data
Files that do not match any of the above patterns are classified based on creation time:
- If the file was created less than 24 hours ago - it is considered test data
- If the file was created more than 24 hours ago - it is considered real data

## Usage

### Automatic Organization
To automatically organize existing files, run the script:

```bash
python scripts/organize_test_data.py
```

### Manual Organization
You can also use the test data manager programmatically:

```python
from src.core.test_data_manager import TestDataManager

# Create manager
manager = TestDataManager("results")

# Organize existing files
manager.organize_existing_files()

# Clean up old test data (default is older than 7 days)
manager.cleanup_old_test_data()

# Remove empty directories
manager._remove_empty_directories()

# Get statistics
stats = manager.get_test_data_stats()
print(f"Test files: {stats['test_files_count']}")
print(f"Real files: {stats['real_files_count']}")
```

## Configuration

You can configure the system's behavior by changing parameters in the TestDataManager constructor:

```python
# Clean up files older than 30 days
manager.cleanup_old_test_data(days_old=30)

# Use a different results directory
manager = TestDataManager("my_results")
```

## Benefits

1. **Improved Organization** - all data is structured by type
2. **Space Saving** - automatic cleanup of old test data
3. **Clean Structure** - automatic removal of empty directories
4. **Easy Navigation** - easier to find the files you need
5. **Automation** - minimal user intervention required
6. **Statistics** - ability to track data volume

## Extending Functionality

To add new classification patterns, edit the file `src/core/test_data_manager.py`:

```python
# List of files that are definitely test data
test_patterns = [
    "*test*",
    "*_тест_*",
    "test_*",
    "*_test_*",
    "*fish_batch_test_results*",
    "*_оптимизация_*"
    # Add new patterns here
]

# List of files that are definitely real data
real_patterns = [
    "*b3ded820-4385-4a42-abc7-75dc0756d335*",
    "*вся номенклатура*"
    # Add new patterns here
]
```