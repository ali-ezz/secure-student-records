import pathlib
import config


def test_config_imports():
    assert hasattr(config, 'DATABASE_PATH')


def test_requirements_file_exists():
    req_path = pathlib.Path(__file__).parent.parent / 'requirements.txt'
    assert req_path.exists()
