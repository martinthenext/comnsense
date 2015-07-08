using System;
using System.Collections.Generic;
using Microsoft.Office.Interop.Excel;

namespace comnsense
{
    [Serializable]
    internal class Event
    {
        public enum EventType
        {
            WorkbookOpen = 0,
            WorkbookBeforeClose = 1,
            SheetChange = 2,
            RangeResponse = 3
        }

        public static Event WorkbookOpen(string ident, Workbook wb)
        {
            return new Event
            {
                type = EventType.WorkbookOpen,
                workbook = ident
            };
        }

        public static Event WorkbookBeforeClose(string ident, Workbook wb)
        {
            return new Event
            {
                type = EventType.WorkbookBeforeClose,
                workbook = ident
            };
        }

        public static Event SheetChange(string ident, Worksheet sh, Range range, Cell[][] prevCells)
        {
            var @event = new Event
            {
                type = EventType.SheetChange,
                workbook = ident,
                sheet = sh.Name,
                cells = GetCellsFromRange(range),
            };


            // Before sending the previous values of Range make sure they have the same dimentions
            if (prevCells.GetLength(0) == @event.cells.GetLength(0))
                @event.prev_cells = prevCells;

            return @event;
        }

        public static Cell[][] GetCellsFromRange(
            Range range, 
            bool border = false,
            bool font = false, 
            bool color = false,
            bool fontstyle = false)
        {
            var list = new List<Cell[]>();
            foreach (Range row in range.Rows)
            {
                var rowlist = new List<Cell>();
                foreach (Range cell in row)
                {
                    string key = "";
                    string value = "";
                    if (cell != null && cell.Address != null)
                        key = cell.Address.ToString();
                    if (cell != null && cell.Value2 != null)
                        value = cell.Value2.ToString();

                    if (key == "")
                        continue;

                    var item = new Cell {key = key, value = value};
                    if (border)
                    {
                        // TODO not implemented
                    }

                    if (cell.Font != null && cell.Font.Name != null && font)
                        item.font = cell.Font.Name.ToString();

                    if (cell.Interior != null && cell.Interior.ColorIndex != null && color)
                        item.color = (byte) cell.Interior.ColorIndex;

                    if (cell.Font != null && fontstyle)
                    {
                        item.fontstyle = 0;
                        if (cell.Font.Bold)
                            item.fontstyle |= 1;
                        if (cell.Font.Italic)
                            item.fontstyle |= 2;
                        if (cell.Font.Underline)
                            item.fontstyle |= 4;
                    }

                    rowlist.Add(item);
                }
                list.Add(rowlist.ToArray());
            }
            return list.ToArray();
        }

        public EventType type;
        public string workbook; // workbook ident
        public string sheet; // sheet name
        public Cell[][] cells; // array of rows of cells
        public Cell[][] prev_cells; // previous cells for cell change events
    }
}