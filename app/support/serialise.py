import csv
import attrs

from io import StringIO
from typing import Dict, Iterable, Type, TypeVar
from cattrs import GenConverter


X = TypeVar("X")


def _attrs_field_alias_map(type_: Type[X]) -> Dict[str, str]:
    return {
        field.name: field.metadata["alias"] if field.metadata else field.name
        # This type issue is because of the use of generics as above.
        for field in attrs.fields(type_)  # type: ignore
    }


def dict_to_attrs(type_: Type[X], rows: Iterable[Dict[str, str]]) -> Iterable[X]:
    # We need to reverse the fields later to assign them as dict keys in the structuring
    # function
    alias_field_map = {val: key for key, val in _attrs_field_alias_map(type_).items()}

    serialised_rows = []
    for row in rows:
        expected_fields = set(alias_field_map.keys())
        actual_fields = set(row.keys())
        if expected_fields - actual_fields != set():
            raise KeyError(
                f"""Fields of {type_.__name__} do not match for row.
                Difference with Expected: {expected_fields - actual_fields}
                Difference with recieved: {actual_fields - expected_fields}
                """
            )
        aliased_row = {alias_field_map[key]: val for key, val in row.items()}
        serialised_rows.append(type_(**aliased_row))

    return serialised_rows


def csv_to_attrs(
    type_: Type[X],
    converter: GenConverter,
    data: bytes,
    encoding: str = "utf-8",
    check_headers: bool = True,
) -> Iterable[X]:
    # We need to reverse the fields later to assign them as dict keys in the structuring
    # function
    alias_field_map = {val: key for key, val in _attrs_field_alias_map(type_).items()}

    serialised_rows = []
    with StringIO(data.decode(encoding)) as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            if not check_headers:
                serialised_rows.append(converter.structure(row, type_))
                continue

            expected_fields = set(alias_field_map.keys())
            actual_fields = set(row.keys())

            # Check the rows column headers are correct
            if expected_fields - actual_fields != set():
                raise KeyError(
                    f"""Fields of {type_.__name__} do not match for row.
                    Difference with Expected: {expected_fields - actual_fields}
                    Difference with recieved: {actual_fields - expected_fields}
                    """
                )
            serialised_rows.append(
                converter.structure(
                    {alias_field_map[key]: val for key, val in row.items()}, type_
                )
            )

    return serialised_rows


def attrs_to_csv(
    type_: Type[X], converter: GenConverter, rows: Iterable[X], encoding: str = "utf-8"
) -> bytes:
    field_alias_map = _attrs_field_alias_map(type_)
    with StringIO() as csvfile:
        writer = csv.DictWriter(csvfile, field_alias_map.values())
        writer.writeheader()
        for row in rows:
            row_dict = {
                field_alias_map[key]: val
                for key, val in converter.unstructure(row).items()
            }
            writer.writerow(row_dict)

        return csvfile.getvalue().encode(encoding)
