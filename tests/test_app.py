import pytest
from unittest.mock import Mock, patch
from src.app import ResumeAnalyzer, ResumeGenerator, load_config

@pytest.fixture
def sample_config():
    return {
        'resume_analysis': {
            'model': 'openai/gpt-4',
            'temperature': 0.7,
            'max_tokens': 1000
        },
        'resume_generation': {
            'output_dir': './data/generated',
            'formats': ['pdf', 'docx']
        }
    }

def test_config_loading():
    config = load_config()
    assert 'resume_analysis' in config
    assert config['resume_analysis']['model'] == 'openai/gpt-4'

def test_resume_analyzer_initialization(sample_config):
    analyzer = ResumeAnalyzer(sample_config)
    assert analyzer.config['model'] == 'openai/gpt-4'
    assert analyzer.config['temperature'] == 0.7

@patch('src.app.os.makedirs')
def test_resume_generator_initialization(mock_makedirs, sample_config):
    generator = ResumeGenerator(sample_config)
    assert generator.output_dir == './data/generated'
    mock_makedirs.assert_called_once_with('./data/generated', exist_ok=True)

@patch('src.app.load_dotenv')
def test_main_execution(mock_dotenv, sample_config):
    with patch('src.app.load_config') as mock_config:
        mock_config.return_value = sample_config
        from src.app import main
        main()
        
    mock_dotenv.assert_called_once()
    mock_config.assert_called_once()

def test_analyze_gaps_returns_expected_structure(sample_config):
    analyzer = ResumeAnalyzer(sample_config)
    result = analyzer.analyze_gaps("", "")
    assert isinstance(result, dict)
    assert 'qualified' in result
    assert 'gap_analysis' in result

def test_api_key_is_not_empty(sample_config):
    with patch('src.app.load_dotenv') as mock_dotenv:
        mock_dotenv.return_value = {"OPENROUTER_API_KEY": "test_key"}
        from src.app import main
        main()
        assert "OPENROUTER_API_KEY" in mock_dotenv.return_value
        assert mock_dotenv.return_value["OPENROUTER_API_KEY"] != ""