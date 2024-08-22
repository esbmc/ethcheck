import xml.etree.ElementTree as ET

def generate_python_script(xml_file, func_name, arg_types, output_file):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        input_elements = root.findall("./input")
        if not input_elements:
            raise ValueError("No <input> nodes are present in the XML file")

        # TODO: Check why ESBMC is adding an extra <input>
        root.remove(input_elements[0])

        inputs = [elem.text for elem in root.findall("./input")]

        if len(inputs) != len(arg_types):
            raise ValueError("The number of input nodes does not match the number of argument types")

        with open(output_file, 'w') as python_script:
            python_script.write("from eth2spec.deneb import mainnet as spec\n")
            python_script.write("from eth2spec.utils.ssz.ssz_typing import uint64\n")
            python_script.write("from eth2spec.deneb.mainnet import Validator\n")
            python_script.write("from eth2spec.deneb.mainnet import Epoch\n")
            python_script.write("from eth2spec.deneb.mainnet import Slot\n")
            python_script.write("from eth2spec.deneb.mainnet import BeaconState\n")
            python_script.write("from eth2spec.deneb.mainnet import BeaconBlock\n")
            python_script.write("from eth2spec.deneb.mainnet import Blob\n")
            python_script.write("from eth2spec.deneb.mainnet import BlobSidecar\n")
            python_script.write("from eth2spec.deneb.mainnet import Root\n")
            python_script.write("from eth2spec.deneb.mainnet import SignedBeaconBlock\n")
            python_script.write("from eth2spec.deneb.mainnet import BLSFieldElement\n")
            python_script.write("from eth2spec.deneb.mainnet import BLSSignature\n")
            python_script.write("from eth2spec.deneb.mainnet import Bytes32\n")
            python_script.write("from eth2spec.deneb.mainnet import Bytes48\n")
            python_script.write("from eth2spec.deneb.mainnet import BlobIndex\n")
            python_script.write("from eth2spec.deneb.mainnet import LightClientUpdate\n")
            python_script.write("from eth2spec.deneb.mainnet import LightClientHeader\n")
            python_script.write("from eth2spec.deneb.mainnet import LightClientStore\n")
            python_script.write("from eth2spec.deneb.mainnet import Store\n")
            python_script.write("from eth2spec.deneb.mainnet import Eth1Block\n")
            python_script.write("from eth2spec.deneb.mainnet import KZGCommitment\n")
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
#     generate_python_script("testcase.xml", "integer_squareroot", "test_consensus.py")
