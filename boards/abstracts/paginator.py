from django.core.paginator import Paginator

PAGINATOR_LOOKAROUND_SIZE = 3


def get_paginator(*args, **kwargs):
    return DividedPaginator(*args, **kwargs)


class DividedPaginator(Paginator):

    lookaround_size = PAGINATOR_LOOKAROUND_SIZE
    current_page = 0

    def center_range(self):
        index = self.page_range.index(self.current_page)

        start = max(0, index - self.lookaround_size)
        end = min(len(self.page_range), index + self.lookaround_size + 1)
        return self.page_range[start:end]
