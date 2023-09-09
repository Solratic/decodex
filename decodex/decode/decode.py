import itertools
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple
from typing import Union

from eth_abi import decode as decode_abi
from eth_utils.abi import collapse_if_tuple


def eth_decode_input(abi: Dict, data: str) -> Tuple[str, Dict]:
    """
    Decodes Ethereum input given the ABI and data.

    Parameters
    ----------
    abi : Dict
        The ABI of the function.
    data : str
        The data associated with the function.

    Returns
    -------
    Tuple[str, Dict]
        The function signature and the parameters decoded from the input.

    """

    # Ensure ABI is a valid function
    if "name" not in abi or abi.get("type") != "function":
        return "{}", {}

    # Separate inputs into indexed and non-indexed
    inputs = abi.get("inputs", [])

    func_signature = [collapse_if_tuple(inp) for inp in inputs]
    text_signature = "{}({})".format(abi["name"], ",".join(func_signature))

    # Decode values from data
    values = decode_abi(func_signature, bytes(bytearray.fromhex(data[10:])))

    # Fill parameters with values
    params = {}
    for idx, val in enumerate(values):
        params.update(process_abi_tuple(inputs[idx], val))

    return text_signature, params


def eth_decode_log(event_abi: Dict, topics: List[str], data: str) -> Tuple[str, Dict]:
    """
    Decodes Ethereum log given the event ABI, topics, and data.

    Parameters
    ----------
    event_abi : Dict
        The ABI of the event.
    topics : List[str]
        The topics associated with the log.
    data : str
        The data associated with the log.

    Returns
    -------
    Tuple[str, Dict]
        The function signature and the parameters decoded from the log.

    """

    # Ensure ABI is a valid event
    if "name" not in event_abi or event_abi.get("type") != "event":
        return "{}", {}

    # Separate indexed and non-indexed inputs
    indexed_inputs, non_indexed_inputs = _partition_inputs(event_abi.get("inputs", []))

    func_signature = _create_function_signature(event_abi["name"], indexed_inputs + non_indexed_inputs)

    indexed_values = _decode_values_from_topics(indexed_inputs, topics)
    non_indexed_values = _decode_values_from_data(non_indexed_inputs, data[2:])

    # Merge indexed and non-indexed values
    parameters = _merge_parameters(indexed_values, non_indexed_values)

    # Convert byte data to hex
    _convert_bytes_to_hex(parameters)

    return func_signature, parameters


def _partition_inputs(inputs: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
    """
    Partitions inputs into indexed and non-indexed inputs.

    Parameters
    ----------
    inputs : List[Dict]
        List of inputs from ABI.

    Returns
    -------
    Tuple[List[Dict], List[Dict]]
        A tuple containing indexed and non-indexed inputs.

    """
    indexed, non_indexed = [], []
    for input in inputs:
        if input.get("indexed"):
            indexed.append(input)
        else:
            non_indexed.append(input)
    return indexed, non_indexed


def _create_function_signature(name: str, inputs: List[Dict]) -> str:
    """
    Creates a function signature string based on the name and inputs.

    Parameters
    ----------
    name : str
        Name of the function.
    inputs : List[Dict]
        List of inputs associated with the function.

    Returns
    -------
    str
        The function signature.

    """
    return "{}({})".format(
        name,
        ", ".join([f"{input['type']} {input.get('name', '')}" for input in inputs]),
    )


def _decode_values_from_topics(indexed_inputs: List[Dict], topics: List[str]) -> Dict:
    """
    Decodes values from topics based on indexed inputs.

    Parameters
    ----------
    indexed_inputs : List[Dict]
        List of indexed inputs.
    topics : List[str]
        List of topics.

    Returns
    -------
    Dict
        A dictionary of decoded values from topics.

    """
    return {
        input["name"]: decode_abi([input["type"]], bytes.fromhex(topic[2:]))[0]
        for input, topic in zip(indexed_inputs, topics[1:])
    }


def _decode_values_from_data(non_indexed_inputs: List[Dict], data: str) -> Dict:
    """
    Decodes values from data based on non-indexed inputs.

    Parameters
    ----------
    non_indexed_inputs : List[Dict]
        List of non-indexed inputs.
    data : str
        The associated data. CAN NOT CONTAINS THE 0x PREFIX.

    Returns
    -------
    Dict
        A dictionary of decoded values from data.

    """
    types = [input["type"] for input in non_indexed_inputs]
    values = decode_abi(types, bytes.fromhex(data))
    return dict(zip((input["name"] for input in non_indexed_inputs), values))


def _merge_parameters(indexed_values: Dict, non_indexed_values: Dict) -> Dict:
    """
    Merges indexed and non-indexed values, and adds index keys.

    Parameters
    ----------
    indexed_values : Dict
        A dictionary of indexed values.
    non_indexed_values : Dict
        A dictionary of non-indexed values.

    Returns
    -------
    Dict
        A merged dictionary of indexed and non-indexed values with index keys.

    """
    merged = indexed_values.copy()
    merged.update(non_indexed_values)
    # Add __idx_ keys
    for idx, key in enumerate(itertools.chain(indexed_values.keys(), non_indexed_values.keys())):
        merged[f"__idx_{idx}"] = merged[key]
    return merged


def _convert_bytes_to_hex(parameters: Dict) -> None:
    """
    Converts bytes data in the parameters dictionary to hexadecimal. (INPLACE)

    Parameters
    ----------
    parameters : Dict
        The dictionary containing parameters.

    Returns
    -------
    None

    """
    for key, val in list(parameters.items()):  # using list to prevent runtime error
        if isinstance(val, (bytes, bytearray)):
            parameters[key] = val.hex()
        elif isinstance(val, tuple):
            parameters[key] = tuple(e.hex() if isinstance(e, (bytes, bytearray)) else e for e in val)


def process_abi_tuple(abi: Dict, value: Any) -> Dict:
    """
    Process ABI (Application Binary Interface) and value based on type information.

    Parameters
    ----------
    abi : Dict
        The ABI information as a dictionary, including 'type' and 'name' keys.
    value : Any
        The value to be processed, the type of which depends on the ABI information.

    Returns
    -------
    Dict
        A dictionary containing the processed value(s), with the key as the name from the ABI.

    Notes
    -----
    The function can handle types like 'byte', 'tuple' and their array forms.
    """
    abi_type: str = abi["type"]
    abi_name: str = abi["name"]

    if abi_type.startswith("byte"):
        return process_byte_type(abi_type, abi_name, value)

    if abi_type.startswith("tuple"):
        return process_tuple_type(abi, abi_name, value)

    return {abi_name: value}


def process_byte_type(abi_type: str, abi_name: str, value: Union[bytes, List[bytes]]) -> Dict:
    if abi_type.endswith("]"):
        hex_values = [element.hex() for element in value]
        processed_values = []

        for hex_value in hex_values:
            chunks = divide_into_chunks(hex_value, 64)
            processed_values.extend(chunks)

        return {abi_name: processed_values}

    return {abi_name: value.hex()}


def process_tuple_type(abi: Dict, abi_name: str, value: Any) -> Dict:
    is_array = len(abi["type"]) > len("tuple")
    sub_abis = abi["components"]

    if not is_array:
        processed_value = process_single_tuple(sub_abis, value)
        return {abi_name: processed_value}

    processed_values = [process_single_tuple(sub_abis, sub_value) for sub_value in value]
    return {abi_name: processed_values}


def process_single_tuple(sub_abis: Dict, value: Any) -> Dict:
    processed_value = {}
    for index, sub_abi in enumerate(sub_abis):
        processed_value.update(process_abi_tuple(sub_abi, value[index]))
    return processed_value


def divide_into_chunks(data: str, chunk_size: int) -> list:
    """
    Divide the data into chunks of a given size. The last chunk is zero-padded if needed.

    Parameters:
        data (str): The string data to be chunked.
        chunk_size (int): The size of each chunk.

    Returns:
        list: The list of chunks.
    """
    chunks = [data[i : i + chunk_size] for i in range(0, len(data), chunk_size)]

    if len(chunks[-1]) < chunk_size:
        padding_size = chunk_size - len(chunks[-1])
        chunks[-1] += "0" * padding_size

    return chunks
