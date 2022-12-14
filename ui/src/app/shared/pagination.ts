import { SortByDirection } from '@patternfly/react-table';
import {PaginationProps} from "@patternfly/react-core";

export interface PaginationConfiguration extends PaginationProps {
  limit: number;
  count: number;
  filter?: string;
  sortDirection?: SortByDirection;
}

export const defaultSettings: PaginationConfiguration = {
  limit: 50,
  offset: 0,
  count: 0,
  filter: ''
};

export const getCurrentPage = (limit = 1, offset = 0): number =>
  Math.floor(offset / limit) + 1;

export const getNewPage = (page = 1, offset = 0): number => (page - 1) * offset;
