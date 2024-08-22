FINALIZED_ROOT_GINDEX = GeneralizedIndex(105) #70
CURRENT_SYNC_COMMITTEE_GINDEX = GeneralizedIndex(54) #71
NEXT_SYNC_COMMITTEE_GINDEX = GeneralizedIndex(55) #72

class Epoch(uint64): #80
    pass

class Gwei(uint64): #92
    pass

class BLSFieldElement(uint256): #192
    pass

UINT64_MAX = uint64(2**64 - 1) #213
UINT64_MAX_SQRT = uint64(4294967295) #214
GENESIS_EPOCH = Epoch(0) #216
FAR_FUTURE_EPOCH = Epoch(2**64 - 1) #217
ENDIANNESS = 'little' #221
BLS_MODULUS = 123 #257
KZG_ENDIANNESS = 'big' #263
MAX_EFFECTIVE_BALANCE = Gwei(32000000000) #282
SLOTS_PER_EPOCH = uint64(32) #285
MAX_SEED_LOOKAHEAD = uint64(4) #287
EPOCHS_PER_SYNC_COMMITTEE_PERIOD = uint64(256) #310


class Validator:#(Container): #453
#    pubkey: BLSPubkey
    withdrawal_credentials: Bytes32  # Commitment to pubkey for withdrawals
    effective_balance: Gwei  # Balance at stake
#    slashed: boolean
    slashed: bool
    # Status epochs
    activation_eligibility_epoch: Epoch  # When criteria for activation were met
    activation_epoch: Epoch
    exit_epoch: Epoch
    withdrawable_epoch: Epoch  # When validator can withdraw funds

class BeaconState: #789
    genesis_time: uint64
    genesis_validators_root: Root
    slot: Slot


def ceillog2(x: int) -> uint64: #51
    if x < 1:
        raise ValueError(f"ceillog2 accepts only positive values, x={x}")
    return uint64((x - 1).bit_length())


def floorlog2(x: int) -> uint64: #57
    if x < 1:
        raise ValueError(f"floorlog2 accepts only positive values, x={x}")
    return uint64(x.bit_length() - 1)


def integer_squareroot(n: uint64) -> uint64: #969
    """
    Return the largest integer ``x`` such that ``x**2 <= n``.
    """
    if n == UINT64_MAX:
        return UINT64_MAX_SQRT
    x = n
    y = (x + 1) // 2
    while y < x:
        x = y
        y = (x + n // x) // 2
    return x


def bytes_to_uint64(data: bytes) -> uint64: #990
    """
    Return the integer deserialization of ``data`` interpreted as ``ENDIANNESS``-endian.
    """
    return uint64(int.from_bytes(data, ENDIANNESS))


def saturating_sub(a: int, b: int) -> int: #997
    """
    Computes a - b, saturating at numeric bounds.
    """
    return a - b if a > b else 0


def is_active_validator(validator: Validator, epoch: Epoch) -> bool: #1004
    """
    Check if ``validator`` is active.
    """
    return validator.activation_epoch <= epoch < validator.exit_epoch


def is_eligible_for_activation_queue(validator: Validator) -> bool: #1011
    """
    Check if ``validator`` is eligible to be placed into the activation queue.
    """
    return (
        validator.activation_eligibility_epoch == FAR_FUTURE_EPOCH
        and validator.effective_balance == MAX_EFFECTIVE_BALANCE
    )


def is_slashable_validator(validator: Validator, epoch: Epoch) -> bool: #1033
    """
    Check if ``validator`` is slashable.
    """
    return (not validator.slashed) and (validator.activation_epoch <= epoch < validator.withdrawable_epoch)


def compute_epoch_at_slot(slot: Slot) -> Epoch: #1133
    """
    Return the epoch number at ``slot``.
    """
    return Epoch(slot // SLOTS_PER_EPOCH)


def compute_start_slot_at_epoch(epoch: Epoch) -> Slot: #1140
    """
    Return the start slot of ``epoch``.
    """
    return Slot(epoch * SLOTS_PER_EPOCH)


def compute_activation_exit_epoch(epoch: Epoch) -> Epoch: #1147
    """
    Return the epoch during which validator activations and exits initiated in ``epoch`` take effect.
    """
    return Epoch(epoch + 1 + MAX_SEED_LOOKAHEAD)


def get_current_epoch(state: BeaconState) -> Epoch: #1196
    """
    Return the current epoch.
    """
    return compute_epoch_at_slot(state.slot)


def get_previous_epoch(state: BeaconState) -> Epoch: #1203
    """
    Return the previous epoch (unless the current epoch is ``GENESIS_EPOCH``).
    """
    current_epoch = get_current_epoch(state)
    return GENESIS_EPOCH if current_epoch == GENESIS_EPOCH else Epoch(current_epoch - 1)


def is_shuffling_stable(slot: Slot) -> bool: #2284
    return slot % SLOTS_PER_EPOCH != 0


def compute_sync_committee_period(epoch: Epoch) -> uint64: #3052
    return epoch // EPOCHS_PER_SYNC_COMMITTEE_PERIOD


def finalized_root_gindex_at_slot(slot: Slot) -> GeneralizedIndex: #3299
    # pylint: disable=unused-argument
    return FINALIZED_ROOT_GINDEX


def current_sync_committee_gindex_at_slot(slot: Slot) -> GeneralizedIndex: ##3304
    # pylint: disable=unused-argument
    return CURRENT_SYNC_COMMITTEE_GINDEX


def next_sync_committee_gindex_at_slot(slot: Slot) -> GeneralizedIndex: #3309
    # pylint: disable=unused-argument
    return NEXT_SYNC_COMMITTEE_GINDEX


def get_subtree_index(generalized_index: GeneralizedIndex) -> uint64:
    return uint64(generalized_index % 2**(floorlog2(generalized_index)))


def compute_sync_committee_period_at_slot(slot: Slot) -> uint64: #3426
    return compute_sync_committee_period(compute_epoch_at_slot(slot))


# Polynomial commitments
def is_power_of_two(value: int) -> bool: #4207
    """
    Check if ``value`` is a power of two integer.
    """
    return (value > 0) and (value & (value - 1) == 0)


def hash_to_bls_field(data: bytes) -> BLSFieldElement: #4238
    """
    Hash ``data`` and convert the output to a BLS scalar field element.
    The output is not uniform over the BLS field.
    """
    hashed_data = hash(data)
    return BLSFieldElement(int.from_bytes(hashed_data, KZG_ENDIANNESS)) #% BLS_MODULUS)


def bls_field_to_bytes(x: BLSFieldElement) -> Bytes32: #4257
    return int.to_bytes(x % BLS_MODULUS, 32, KZG_ENDIANNESS)

