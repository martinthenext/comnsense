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
        [NonSerialized()]
        public static enum EventType
        {
            WorkbookOpen,
            WorkbookBeforeClose,
            SheetChange
        }

        public static Event WorkbookOpen(Excel.Workbook wb)
        {
            Event evt = new Event { 
                type = EventType.WorkbookOpen, 
                ident = new Ident(wb).ToString() 
            };
            return evt;
        }

        public static Event WorkbookBeforeClose(Excel.Workbook wb)
        {
            Event evt = new Event { 
                type = EventType.WorkbookBeforeClose, 
                ident = new Ident(wb).ToString() 
            };
            return evt;
        }

        public static Event SheetChange(Excel.Worksheet sh, Excel.Range range)
        {
            List<KeyValuePair<String, String>> list = new List<KeyValuePair<string,string>>();
            Event evt = new Event { 
                type = EventType.SheetChange,
                ident = new Ident((sh.Parent as Excel.Workbook)).ToString(),
                sheet = sh.Name
            };
            foreach (Excel.Range cell in range.Cells)
            {
                list.Add(new KeyValuePair<string, string>(cell.Address, cell.Value2));
            }
            evt.values = list.ToArray();
            return evt;
        }

        public EventType type;
        public String ident; // workbook ident
        public String sheet; // sheet name
        public KeyValuePair<String, String>[] values; // values
    }
}
