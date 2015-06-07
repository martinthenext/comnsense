using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Excel = Microsoft.Office.Interop.Excel;

namespace comnsense
{
    [Serializable()]
    class Event
    {
        public enum EventType
        {
            WorkbookOpen = 0,
            WorkbookBeforeClose = 1,
            SheetChange = 2
        }

        public static Event WorkbookOpen(String ident, Excel.Workbook wb)
        {
            Event evt = new Event { 
                type = EventType.WorkbookOpen, 
                workbook = ident 
            };
            return evt;
        }

        public static Event WorkbookBeforeClose(String ident, Excel.Workbook wb)
        {
            Event evt = new Event { 
                type = EventType.WorkbookBeforeClose, 
                workbook = ident 
            };
            return evt;
        }

        public static Event SheetChange(String ident, Excel.Worksheet sh, Excel.Range range)
        {
            Event evt = new Event { 
                type = EventType.SheetChange,
                workbook = ident,
                sheet = sh.Name
            };
            
            evt.cells = GetCellsFromRange(range);
            return evt;
        }

        private static Cell[][] GetCellsFromRange(Excel.Range range, bool border = false, 
                                                  bool font = false, bool color = false,
                                                  bool fontstyle = false) 
        {
            List<Cell[]> list = new List<Cell[]>();
            foreach (Excel.Range row in range.Rows)
            {
                List<Cell> rowlist = new List<Cell>();
                foreach (Excel.Range cell in row) {
                    String key = "";
                    String value = "";
                    if ((cell != null) && (cell.Address != null))
                    {
                        key = cell.Address.ToString();
                    }
                    if ((cell != null) && (cell.Value2 != null))
                    {
                        value = cell.Value2.ToString();
                    }
                    if (key != "")
                    {
                        Cell item = new Cell { key = key, value = value };
                        if (border)
                        {
                            // not implemented
                        }
                        if ((cell.Font != null) && (cell.Font.Name != null) && font)
                        {
                            item.font = cell.Font.Name.ToString();
                        }
                        if ((cell.Interior != null) && (cell.Interior.ColorIndex != null) && color)
                        {
                            item.color = (int)cell.Interior.ColorIndex;
                        }
                        if ((cell.Font != null) && fontstyle)
                        {
                            item.fontstyle = 0;
                            if (cell.Font.Bold)
                            {
                                item.fontstyle |= 1;
                            }
                            if (cell.Font.Italic)
                            {
                                item.fontstyle |= 2;
                            }
                            if (cell.Font.Underline)
                            {
                                item.fontstyle |= 4;
                            }
                        }
                        rowlist.Add(item);
                    }
                }
                list.Add(rowlist.ToArray());
            }
            return list.ToArray();

        }

        public EventType type;
        public String workbook; // workbook ident
        public String sheet; // sheet name
        public Cell[][] cells; // array of rows of cells
    }
}