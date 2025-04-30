import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import yaml
import subprocess
from firewheel.control.model_component_install import ModelComponentInstall, InstallPrompt

@pytest.fixture
def mock_model_component():
    class MockModelComponent:
        def __init__(self, name, path):
            self.name = name
            self.path = path

    return MockModelComponent(name="test_mc", path="/mock/path")

@pytest.fixture
def install_component(mock_model_component):
    return ModelComponentInstall(mc=mock_model_component)

@patch('firewheel.control.model_component_install.Path.open', new_callable=MagicMock)
@patch('firewheel.control.model_component_install.Path.stat', return_value=MagicMock(st_mode=0))
@patch('firewheel.control.model_component_install.Path.chmod')
def test_install_mc_success(mock_chmod, mock_stat, mock_open, install_component):
    # Mock the behavior of the file read to simulate a valid INSTALL script
    mock_file = MagicMock()
    mock_file.read.return_value = "#!/bin/bash\necho 'Installing...'"
    mock_open.return_value.__enter__.return_value = mock_file  # Simulate the context manager

    with patch('firewheel.control.model_component_install.subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        result = install_component.install_mc("test_mc", Path("/mock/path/INSTALL"))
        assert result is True

@patch('firewheel.control.model_component_install.Path.open', new_callable=MagicMock)
@patch('firewheel.control.model_component_install.Path.stat', return_value=MagicMock(st_mode=0))
@patch('firewheel.control.model_component_install.Path.chmod')
def test_install_mc_failure(mock_chmod, mock_stat, mock_open, install_component):
    # Mock the behavior of the file read to simulate a valid INSTALL script
    mock_file = MagicMock()
    mock_file.read.return_value = "#!/bin/bash\necho 'Installing...'"
    mock_open.return_value.__enter__.return_value = mock_file  # Simulate the context manager

    with patch('firewheel.control.model_component_install.subprocess.run') as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(1, 'cmd')
        result = install_component.install_mc("test_mc", Path("/mock/path/INSTALL"))
        assert result is False

@patch('firewheel.control.model_component_install.Path.open', new_callable=MagicMock)
@patch('firewheel.control.model_component_install.Path.stat', return_value=MagicMock(st_mode=0))
@patch('firewheel.control.model_component_install.Path.chmod')
def test_install_mc_already_installed(mock_chmod, mock_stat, mock_open, install_component):
    # Mock the behavior of the file read to simulate a valid INSTALL script
    mock_file = MagicMock()
    mock_file.read.return_value = "#!/bin/bash\necho 'Installing...'"
    mock_open.return_value.__enter__.return_value = mock_file  # Simulate the context manager

    with patch('firewheel.control.model_component_install.subprocess.run') as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(117, 'cmd')
        result = install_component.install_mc("test_mc", Path("/mock/path/INSTALL"))
        assert result is True

@patch('yaml.safe_load', return_value=[{'hosts': 'localhost'}])
@patch('firewheel.control.model_component_install.Path.open', new_callable=MagicMock)
def test_is_ansible_playbook_valid(mock_open, mock_yaml, install_component):
    # Mock the behavior of the file read to simulate a valid Ansible playbook
    mock_file = MagicMock()
    mock_file.read.return_value = "---\n- hosts: localhost"
    mock_open.return_value.__enter__.return_value = mock_file  # Simulate the context manager

    result = install_component.is_ansible_playbook(Path("/mock/path/INSTALL"))
    assert result is True

@patch('yaml.safe_load', side_effect=yaml.YAMLError)
@patch('firewheel.control.model_component_install.Path.open', new_callable=MagicMock)
def test_is_ansible_playbook_invalid(mock_open, mock_yaml, install_component):
    # Mock the behavior of the file read to simulate invalid YAML
    mock_file = MagicMock()
    mock_file.read.return_value = "invalid yaml"
    mock_open.return_value.__enter__.return_value = mock_file  # Simulate the context manager

    result = install_component.is_ansible_playbook(Path("/mock/path/INSTALL"))
    assert result is False

@patch('firewheel.control.model_component_install.Path.open', new_callable=MagicMock)
def test_is_ansible_playbook_invalid_format(mock_open, install_component):
    # Mock the behavior of the file read to simulate invalid YAML
    mock_file = MagicMock()
    mock_file.read.return_value = "invalid yaml"
    mock_open.return_value.__enter__.return_value = mock_file

    result = install_component.is_ansible_playbook(Path("/mock/path/INSTALL"))
    assert result is False  # Expecting False due to invalid YAML


@patch('firewheel.control.model_component_install.Path.exists', side_effect=[False])
def test_run_install_script_no_install_script(mock_exists, install_component):
    result = install_component.run_install_script()
    assert result is True  # Expecting True since the install script does not exist

@patch('firewheel.control.model_component_install.Path.exists', side_effect=[True, True])  # install_script exists, install_flag exists
def test_run_install_script_with_existing_install_flag(mock_exists, install_component):
    result = install_component.run_install_script()
    assert result is True  # Expecting True since the install flag exists

def test_model_component_install_init_raises_value_error():
    with pytest.raises(ValueError, match="Must specify a Model Component."):
        ModelComponentInstall()  # Pass nothing to trigger the ValueError


@patch('firewheel.control.model_component_install.Path.exists', side_effect=[True, False])  # install_script exists, install_flag does not exist
@patch('firewheel.control.model_component_install.InstallPrompt.ask', return_value='y')  # Simulate user input
@patch('firewheel.control.model_component_install.ModelComponentInstall.install_mc', return_value=False)  # Mock install_mc to return True
def test_run_install_script_user_prompt(mock_install_mc, mock_ask, mock_exists, install_component):
    result = install_component.run_install_script()
    assert result is False

@patch('firewheel.control.model_component_install.Path.exists', side_effect=[True, False])  # install_script exists, install_flag does not exist
@patch('firewheel.control.model_component_install.ModelComponentInstall.install_mc', return_value=False)
def test_run_install_script_insecure_fail(mock_install_mc, mock_exists, install_component):
    result = install_component.run_install_script(insecure=True)
    assert result is False

@patch('firewheel.control.model_component_install.Path.exists', side_effect=[True, False])  # install_script exists, install_flag does not exist
@patch('firewheel.control.model_component_install.ModelComponentInstall.install_mc', return_value=True)
def test_run_install_script_insecure_pass(mock_install_mc, mock_exists, install_component):
    result = install_component.run_install_script(insecure=True)
    assert result is True
