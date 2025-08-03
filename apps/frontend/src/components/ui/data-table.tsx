"use client"

import * as React from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Badge } from "@/components/ui/badge"
import { 
  Search, 
  Filter, 
  Download,
  Trash2,
  ChevronLeft,
  ChevronRight
} from "lucide-react"

interface Column {
  key: string
  label: string
  sortable?: boolean
  filterable?: boolean
  render?: (value: any, row: any) => React.ReactNode
}

interface DataTableProps {
  columns: Column[]
  data: any[]
  searchKey?: string
  onSearch?: (value: string) => void
  onBulkDelete?: (ids: string[]) => void
  onBulkExport?: (ids: string[]) => void
  showActions?: boolean
  showFilters?: boolean
  showPagination?: boolean
  pageSize?: number
}

export function DataTable({
  columns,
  data,
  searchKey,
  onSearch,
  onBulkDelete,
  onBulkExport,
  showActions = true,
  showFilters = true,
  showPagination = true,
  pageSize = 10,
}: DataTableProps) {
  const [currentPage, setCurrentPage] = React.useState(1)
  const [searchTerm, setSearchTerm] = React.useState("")
  const [selectedRows, setSelectedRows] = React.useState<Set<string>>(new Set())
  const [visibleColumns, setVisibleColumns] = React.useState<Set<string>>(
    new Set(columns.map(col => col.key))
  )

  // Filter data based on search term
  const filteredData = React.useMemo(() => {
    if (!searchTerm) return data
    
    return data.filter((row) => {
      return columns.some((column) => {
        const value = row[column.key]
        if (value == null) return false
        return String(value).toLowerCase().includes(searchTerm.toLowerCase())
      })
    })
  }, [data, searchTerm, columns])

  // Paginate data
  const paginatedData = React.useMemo(() => {
    if (!showPagination) return filteredData
    
    const startIndex = (currentPage - 1) * pageSize
    const endIndex = startIndex + pageSize
    return filteredData.slice(startIndex, endIndex)
  }, [filteredData, currentPage, pageSize, showPagination])

  const totalPages = Math.ceil(filteredData.length / pageSize)

  const handleSearch = (value: string) => {
    setSearchTerm(value)
    setCurrentPage(1) // Reset to first page when searching
    onSearch?.(value)
  }

  const handleRowSelect = (rowId: string, checked: boolean) => {
    const newSelected = new Set(selectedRows)
    if (checked) {
      newSelected.add(rowId)
    } else {
      newSelected.delete(rowId)
    }
    setSelectedRows(newSelected)
  }

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      setSelectedRows(new Set(paginatedData.map(row => row.id)))
    } else {
      setSelectedRows(new Set())
    }
  }

  const handleBulkDelete = () => {
    if (onBulkDelete && selectedRows.size > 0) {
      onBulkDelete(Array.from(selectedRows))
      setSelectedRows(new Set())
    }
  }

  const handleBulkExport = () => {
    if (onBulkExport && selectedRows.size > 0) {
      onBulkExport(Array.from(selectedRows))
    }
  }

  const renderCell = (column: Column, row: any) => {
    const value = row[column.key]
    
    if (column.render) {
      return column.render(value, row)
    }
    
    return value != null ? String(value) : ""
  }

  return (
    <div className="space-y-4">
      {/* Search and Filters */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          {searchKey && (
            <div className="relative">
              <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder={`Search ${searchKey}...`}
                value={searchTerm}
                onChange={(event) => handleSearch(event.target.value)}
                className="pl-8 w-[300px]"
              />
            </div>
          )}
          
          {showFilters && (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" className="ml-auto">
                  <Filter className="mr-2 h-4 w-4" />
                  Columns
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                {columns.map((column) => (
                  <DropdownMenuCheckboxItem
                    key={column.key}
                    checked={visibleColumns.has(column.key)}
                    onCheckedChange={(checked: boolean) => {
                      const newVisible = new Set(visibleColumns)
                      if (checked) {
                        newVisible.add(column.key)
                      } else {
                        newVisible.delete(column.key)
                      }
                      setVisibleColumns(newVisible)
                    }}
                  >
                    {column.label}
                  </DropdownMenuCheckboxItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>
          )}
        </div>

        {/* Bulk Actions */}
        {showActions && selectedRows.size > 0 && (
          <div className="flex items-center space-x-2">
            <Badge variant="secondary">
              {selectedRows.size} selected
            </Badge>
            {onBulkExport && (
              <Button
                variant="outline"
                size="sm"
                onClick={handleBulkExport}
              >
                <Download className="mr-2 h-4 w-4" />
                Export
              </Button>
            )}
            {onBulkDelete && (
              <Button
                variant="destructive"
                size="sm"
                onClick={handleBulkDelete}
              >
                <Trash2 className="mr-2 h-4 w-4" />
                Delete
              </Button>
            )}
          </div>
        )}
      </div>

      {/* Table */}
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              {showActions && (
                <TableHead className="w-12">
                  <input
                    type="checkbox"
                    checked={selectedRows.size === paginatedData.length && paginatedData.length > 0}
                    onChange={(e) => handleSelectAll(e.target.checked)}
                    className="rounded border-gray-300"
                  />
                </TableHead>
              )}
              {columns
                .filter(column => visibleColumns.has(column.key))
                .map((column) => (
                  <TableHead key={column.key}>
                    {column.label}
                  </TableHead>
                ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {paginatedData.length > 0 ? (
              paginatedData.map((row) => (
                <TableRow key={row.id}>
                  {showActions && (
                    <TableCell>
                      <input
                        type="checkbox"
                        checked={selectedRows.has(row.id)}
                        onChange={(e) => handleRowSelect(row.id, e.target.checked)}
                        className="rounded border-gray-300"
                      />
                    </TableCell>
                  )}
                  {columns
                    .filter(column => visibleColumns.has(column.key))
                    .map((column) => (
                      <TableCell key={column.key}>
                        {renderCell(column, row)}
                      </TableCell>
                    ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell
                  colSpan={columns.length + (showActions ? 1 : 0)}
                  className="h-24 text-center"
                >
                  No results.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      {/* Pagination */}
      {showPagination && totalPages > 1 && (
        <div className="flex items-center justify-between space-x-2 py-4">
          <div className="flex-1 text-sm text-muted-foreground">
            {selectedRows.size} of {filteredData.length} row(s) selected.
          </div>
          <div className="space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
              disabled={currentPage === 1}
            >
              <ChevronLeft className="mr-2 h-4 w-4" />
              Previous
            </Button>
            <span className="px-2 text-sm">
              Page {currentPage} of {totalPages}
            </span>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
              disabled={currentPage === totalPages}
            >
              Next
              <ChevronRight className="ml-2 h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  )
} 