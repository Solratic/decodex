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
    text_signature = "{}({})".format(abi.get("name", ""), ",".join(func_signature))

    # Decode values from data
    values = decode_abi(func_signature, bytes(bytearray.fromhex(data[10:])))

    # Fill parameters with values
    params = {}
    for idx, val in enumerate(values):
        params.update(_process_abi_tuple(inputs[idx], val))

    return text_signature, params


def _process_abi_tuple(abi: Dict, value: Any) -> Dict:
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
        return _process_byte_type(abi_type, abi_name, value)

    if abi_type.startswith("tuple"):
        return _process_tuple_type(abi, abi_name, value)

    return {abi_name: value}


def _process_byte_type(abi_type: str, abi_name: str, value: Union[bytes, List[bytes]]) -> Dict:
    if abi_type.endswith("]"):
        hex_values = [element.hex() for element in value]
        processed_values = []

        for hex_value in hex_values:
            chunks = _divide_into_chunks(hex_value, 64)
            processed_values.extend(chunks)

        return {abi_name: processed_values}

    return {abi_name: value.hex()}


def _process_tuple_type(abi: Dict, abi_name: str, value: Any) -> Dict:
    is_array = len(abi["type"]) > len("tuple")
    sub_abis = abi["components"]

    if not is_array:
        processed_value = _process_single_tuple(sub_abis, value)
        return {abi_name: processed_value}

    processed_values = [_process_single_tuple(sub_abis, sub_value) for sub_value in value]
    return {abi_name: processed_values}


def _process_single_tuple(sub_abis: Dict, value: Any) -> Dict:
    processed_value = {}
    for index, sub_abi in enumerate(sub_abis):
        processed_value.update(_process_abi_tuple(sub_abi, value[index]))
    return processed_value


def _divide_into_chunks(data: str, chunk_size: int) -> list:
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


def eth_decode_log(event_abi: Dict, topics: List[str], data: str) -> Tuple[str, Dict]:
    """
    Decodes Ethereum log given the event ABI, topics, and data.
    """

    # Ensure ABI is a valid event
    if "name" not in event_abi or event_abi.get("type") != "event":
        return "{}", {}

    inputs: List = event_abi.get("inputs", [])

    # Separate indexed and non-indexed inputs
    indexed_types, non_indexed_types = [], []
    indexed_idx, non_indexed_idx = [], []
    for idx, inp in enumerate(inputs):
        if inp.get("indexed"):
            indexed_types.append(collapse_if_tuple(inp))
            indexed_idx.append(idx)
        else:
            non_indexed_types.append(collapse_if_tuple(inp))
            non_indexed_idx.append(idx)

    indexed_values = decode_abi(indexed_types, bytes(bytearray.fromhex("".join(t[2:] for t in topics[1:]))))
    non_indexed_values = decode_abi(non_indexed_types, bytes(bytearray.fromhex(data[2:])))

    params = {}
    for idx, value in zip(indexed_idx, indexed_values):
        single_param = _process_abi_tuple(inputs[idx], value)
        params.update(single_param)
        params.update({f"__idx_{idx}": list(single_param.values())[0]})
    for idx, value in zip(non_indexed_idx, non_indexed_values):
        single_param = _process_abi_tuple(inputs[idx], value)
        params.update(single_param)
        params.update({f"__idx_{idx}": list(single_param.values())[0]})

    func_signature = [collapse_if_tuple(inp) for inp in inputs]
    text_signature = "{}({})".format(event_abi.get("name", ""), ",".join(func_signature))

    return text_signature, params
