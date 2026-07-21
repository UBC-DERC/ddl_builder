# tests/test_output_yaml.py
import os
import subprocess
from pathlib import Path
import yaml

EXAMPLE = Path("examples/output.yaml")
GOLDEN = Path("tests/golden/output.yaml")

def test_input_yaml_matches_golden(tmp_path):                                                                                                                               
    output: Path = tmp_path / "output.yaml"                                                                                                                                       
    subprocess.run(                                                                                                                                                         
        args=["data-model", str(object=EXAMPLE),                                                                                                                                        
        "--docs", str(object=tmp_path / "docs"),                                                                                                                                  
        "--output", str(object=output)],                                                                                                                                          
        check=True,                                                                                                                                                         
    )                                                                                                                                                                       
                                                                                                                                                                            
    produced: dict = yaml.safe_load(stream=output.read_text())                                                                                                                           
                                                                                                                                                                            
    if os.environ.get(key="UPDATE_GOLDEN"):                                                                                                                                     
        GOLDEN.parent.mkdir(parents=True, exist_ok=True)                                                                                                                    
        GOLDEN.write_text(data=yaml.safe_dump(data=produced, sort_keys=True))                                                                                                         
                                                                                                                                                                            
    expected: dict = yaml.safe_load(stream=GOLDEN.read_text())                                                                                                                           
    assert produced == expected 