import xml.etree.ElementTree as ET

fork_name = None
module_name = None

def generate_python_script(xml_file, func_name, arg_types, output_file):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        inputs = [elem.text for elem in root.findall("./input")]

        # ESBMC versions differ: older builds emit a spurious leading <input>
        # (so N args -> N+1 inputs), while ESBMC 8.3.0 emits exactly one per
        # argument. Align by taking the last len(arg_types) inputs, which is
        # correct for both formats.
        if len(inputs) < len(arg_types):
            raise ValueError("The number of input nodes does not match the number of argument types")
        inputs = inputs[len(inputs) - len(arg_types):]

        with open(output_file, 'w') as python_script:
            python_script.write(f"from eth2spec.{fork_name} import {module_name} as spec\n")
            python_script.write("from eth2spec.utils.ssz.ssz_typing import uint64\n")
            python_script.write(f"from eth2spec.{fork_name}.{module_name} import Validator\n")
            python_script.write(f"from eth2spec.{fork_name}.{module_name} import Epoch\n")
            python_script.write(f"from eth2spec.{fork_name}.{module_name} import Slot\n")
            python_script.write(f"from eth2spec.{fork_name}.{module_name} import BeaconState\n")
            python_script.write(f"from eth2spec.{fork_name}.{module_name} import BeaconBlock\n")
            if (module_name == 'deneb'):
                python_script.write(f"from eth2spec.{fork_name}.{module_name} import Blob\n")
                python_script.write(f"from eth2spec.{fork_name}.{module_name} import BlobSidecar\n")
                python_script.write(f"from eth2spec.{fork_name}.{module_name} import BLSFieldElement\n")
                python_script.write(f"from eth2spec.{fork_name}.{module_name} import BlobIndex\n")
                python_script.write(f"from eth2spec.{fork_name}.{module_name} import LightClientUpdate\n")
                python_script.write(f"from eth2spec.{fork_name}.{module_name} import LightClientHeader\n")
                python_script.write(f"from eth2spec.{fork_name}.{module_name} import LightClientStore\n")
                python_script.write(f"from eth2spec.{fork_name}.{module_name} import KZGCommitment\n")
            python_script.write(f"from eth2spec.{fork_name}.{module_name} import Root\n")
            python_script.write(f"from eth2spec.{fork_name}.{module_name} import SignedBeaconBlock\n")
            python_script.write(f"from eth2spec.{fork_name}.{module_name} import BLSSignature\n")
            python_script.write(f"from eth2spec.{fork_name}.{module_name} import Bytes32\n")
            python_script.write(f"from eth2spec.{fork_name}.{module_name} import Bytes48\n")
            python_script.write(f"from eth2spec.{fork_name}.{module_name} import Store\n")
            python_script.write(f"from eth2spec.{fork_name}.{module_name} import Eth1Block\n")
            python_script.write("\n")
            python_script.write("def test_my_func():\n")

            params = ", ".join([f"{arg_type}({val})" for arg_type, val in zip(arg_types, inputs)])
            #python_script.write("  try:\n")
            python_script.write(f"    spec.{func_name}({params})\n")
            #python_script.write("  except ValueError:\n")
            #python_script.write("     pass\n")

    except ET.ParseError as e:
        print(f"Error parsing the XML: {e}")
    except IOError as e:
        print(f"Error accessing the file: {e}")

# if __name__ == "__main__":
#     generate_python_script("testcase.xml", "phase0", "integer_squareroot", "test_consensus.py")
