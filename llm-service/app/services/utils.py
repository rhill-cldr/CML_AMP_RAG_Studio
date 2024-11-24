# ##############################################################################
#  CLOUDERA APPLIED MACHINE LEARNING PROTOTYPE (AMP)
#  (C) Cloudera, Inc. 2024
#  All rights reserved.
#
#  Applicable Open Source License: Apache 2.0
#
#  NOTE: Cloudera open source products are modular software products
#  made up of hundreds of individual components, each of which was
#  individually copyrighted.  Each Cloudera open source product is a
#  collective work under U.S. Copyright Law. Your license to use the
#  collective work is as provided in your written agreement with
#  Cloudera.  Used apart from the collective work, this file is
#  licensed for your use pursuant to the open source license
#  identified above.
#
#  This code is provided to you pursuant a written agreement with
#  (i) Cloudera, Inc. or (ii) a third-party authorized to distribute
#  this code. If you do not have a written agreement with Cloudera nor
#  with an authorized and properly licensed third party, you do not
#  have any rights to access nor to use this code.
#
#  Absent a written agreement with Cloudera, Inc. (“Cloudera”) to the
#  contrary, A) CLOUDERA PROVIDES THIS CODE TO YOU WITHOUT WARRANTIES OF ANY
#  KIND; (B) CLOUDERA DISCLAIMS ANY AND ALL EXPRESS AND IMPLIED
#  WARRANTIES WITH RESPECT TO THIS CODE, INCLUDING BUT NOT LIMITED TO
#  IMPLIED WARRANTIES OF TITLE, NON-INFRINGEMENT, MERCHANTABILITY AND
#  FITNESS FOR A PARTICULAR PURPOSE; (C) CLOUDERA IS NOT LIABLE TO YOU,
#  AND WILL NOT DEFEND, INDEMNIFY, NOR HOLD YOU HARMLESS FOR ANY CLAIMS
#  ARISING FROM OR RELATED TO THE CODE; AND (D)WITH RESPECT TO YOUR EXERCISE
#  OF ANY RIGHTS GRANTED TO YOU FOR THE CODE, CLOUDERA IS NOT LIABLE FOR ANY
#  DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, PUNITIVE OR
#  CONSEQUENTIAL DAMAGES INCLUDING, BUT NOT LIMITED TO, DAMAGES
#  RELATED TO LOST REVENUE, LOST PROFITS, LOSS OF INCOME, LOSS OF
#  BUSINESS ADVANTAGE OR UNAVAILABILITY, OR LOSS OR CORRUPTION OF
#  DATA.
# ##############################################################################

import re
from typing import Generator, List, Sequence, Tuple, TypeVar, Union

# TODO delete this if it's not being used


def parse_choice_select_answer_fn(
    answer: str, num_choices: int, raise_error: bool = False
) -> Tuple[List[int], List[float]]:
    """Default parse choice select answer function."""
    answer_lines = answer.split("\n")
    answer_nums = []
    answer_relevances = []
    valid_answer_lines = []
    for answer_line in answer_lines:
        if "None" in answer_line.strip():
            continue
        if answer_line.strip().startswith("Doc:"):
            valid_answer_lines.append(answer_line)
    print(valid_answer_lines)
    if not valid_answer_lines:
        return [], []
    for answer_line in valid_answer_lines:
        line_tokens = answer_line.split(",")
        if len(line_tokens) != 2:
            if not raise_error:
                continue
            else:
                raise ValueError(
                    f"Invalid answer line: {answer_line}. "
                    "Answer line must be of the form: "
                    "answer_num: <int>, answer_relevance: <float>"
                )
        answer_num = int(line_tokens[0].split(":")[1].strip())
        if answer_num > num_choices:
            continue
        answer_nums.append(answer_num)
        # extract just the first digits after the colon.
        _answer_relevance = re.findall(r"\d+", line_tokens[1].split(":")[1].strip())[0]
        answer_relevances.append(float(_answer_relevance))
    return answer_nums, answer_relevances


def get_last_segment(path: str) -> str:
    return path.split("/")[-1]


T = TypeVar("T")


def batch_sequence(
    sequence: Union[Sequence[T], Generator[T, None, None]], batch_size: int
) -> Generator[List[T], None, None]:
    batch = []
    for val in sequence:
        batch.append(val)
        if len(batch) == batch_size:
            yield batch
            batch = []
    if batch:
        yield batch


def flatten_sequence(
    sequence: Union[Sequence[Sequence[T]], Generator[Sequence[T], None, None]],
) -> Generator[T, None, None]:
    for sublist in sequence:
        for item in sublist:
            yield item
