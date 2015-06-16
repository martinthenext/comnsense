using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Excel = Microsoft.Office.Interop.Excel;
using ZeroMQ;
using System.Threading;
using Json = Newtonsoft.Json;

namespace comnsense
{
    class Router
    {
        public const string Address = "tcp://127.0.0.1:8888";
        public static TimeSpan Interval = TimeSpan.FromMilliseconds(500);

        private ZContext ctx;
        private String ident;
        private Excel.Application excel;

        public Router(ZContext ctx, Excel.Application excel, String ident)
        {
            this.ctx = ctx;
            this.excel = excel;
            this.ident = ident;
        }

        public static string FrameToUnicodeString(ZFrame frame)
        {
            long len = frame.Length;
            byte[] bytes = new byte[len];
            for (int i = 0; i < len; i++)
            {
                bytes[i] = (byte)frame.ReadByte();
            }
            return Encoding.UTF8.GetString(bytes);
        }

        public static bool BitToBool(byte bitmask, int position)
        {
            return (bitmask & (1 << position)) != 0;
        }

        private Excel.Workbook GetWorkbook() 
        {
            foreach (Excel.Workbook wb in this.excel.Workbooks)
            {
                Ident id = new Ident(wb);
                if (ident == id.ToString())
                {
                    return wb;
                }
            }
            return null;
        }

        // TODO refactor, this is awful
        private void ApplyBorders(Borders borders, Excel.Range range)
        {
            if (borders.right != null)
            {
                Excel.XlBorderWeight weight = (Excel.XlBorderWeight)borders.right[0];
                range.Borders[Excel.XlBordersIndex.xlEdgeRight].Weight = weight;

                Excel.XlLineStyle lineStyle = (Excel.XlLineStyle)borders.right[1];
                range.Borders[Excel.XlBordersIndex.xlEdgeRight].LineStyle = lineStyle;
            }

            if (borders.left != null)
            {
                Excel.XlBorderWeight weight = (Excel.XlBorderWeight)borders.left[0];
                range.Borders[Excel.XlBordersIndex.xlEdgeLeft].Weight = weight;

                Excel.XlLineStyle lineStyle = (Excel.XlLineStyle)borders.left[1];
                range.Borders[Excel.XlBordersIndex.xlEdgeLeft].LineStyle = lineStyle;
            }

            if (borders.top != null)
            {
                Excel.XlBorderWeight weight = (Excel.XlBorderWeight)borders.top[0];
                range.Borders[Excel.XlBordersIndex.xlEdgeTop].Weight = weight;

                Excel.XlLineStyle lineStyle = (Excel.XlLineStyle)borders.top[1];
                range.Borders[Excel.XlBordersIndex.xlEdgeTop].LineStyle = lineStyle;
            }

            if (borders.bottom != null)
            {
                Excel.XlBorderWeight weight = (Excel.XlBorderWeight)borders.bottom[0];
                range.Borders[Excel.XlBordersIndex.xlEdgeBottom].Weight = weight;

                Excel.XlLineStyle lineStyle = (Excel.XlLineStyle)borders.bottom[1];
                range.Borders[Excel.XlBordersIndex.xlEdgeBottom].LineStyle = lineStyle;
            }
        }

        private void ApplyChange(Action action) {
            this.excel.EnableEvents = false;
            try
            {
                if (action.workbook != ident)
                {
                    return;
                }
                Excel.Workbook wb = GetWorkbook();
                Excel.Worksheet ws = wb.Worksheets[action.sheet];
                foreach (Cell[] row in action.cells)
                {
                    foreach (Cell cell in row)
                    {
                        Excel.Range range = ws.get_Range(cell.key);
                        range.Value2 = cell.value;

                        // Applying cell properties
                        // Matching Event.cs:90

                        if (cell.color != null)
                        {
                            range.Interior.ColorIndex = cell.color;
                        }
                        if (cell.font != null)
                        {
                            range.Font.Name = cell.font;
                        }
                        if (cell.fontstyle != null)
                        {
                            // Parsing format bitmask

                            range.Font.Bold = BitToBool(cell.fontstyle, 0);
                            range.Font.Italic = BitToBool(cell.fontstyle, 1);
                            range.Font.Underline = BitToBool(cell.fontstyle, 2);
                        }
                        if (cell.borders != null)
                        {
                            ApplyBorders(cell.borders, range);
                        }
                    }
                }
            }
            finally
            {
                this.excel.EnableEvents = true;
            }
        }

        public void Run(CancellationToken ct)
        {
            using (ZSocket subscriber = new ZSocket(this.ctx, ZSocketType.SUB),
                           agent = new ZSocket(this.ctx, ZSocketType.DEALER))
            {
                subscriber.SetOption(ZSocketOption.SUBSCRIBE, this.ident);  // any events
                subscriber.Connect(EventPublisher.Address);

                agent.SetOption(ZSocketOption.IDENTITY, Guid.NewGuid().ToString());
                agent.Connect(Router.Address);

                ZError error = default(ZError);
                ZMessage[] messages = null;

                ZSocket[] sockets = new ZSocket[] { 
                    subscriber, agent };

                ZPollItem[] polls = new ZPollItem[] {
                    ZPollItem.Create((ZSocket sock, out ZMessage msg, out ZError err) => {
                        msg = sock.ReceiveMessage();
                        // We need the second frame
                        ZFrame frame = msg.Last();
                        // String frame_str = frame.ReadString(Encoding.UTF8);
                        
                        // Sending the received frame directly
                        using (var message = new ZMessage())
                        {
                            message.Add(new ZFrame("event"));
                            message.Add(frame);
                            agent.Send(message);
                        }
                        err = default(ZError);
                        return true; 
                    }), 
                    ZPollItem.Create((ZSocket sock, out ZMessage msg, out ZError err) => {
                        msg = sock.ReceiveMessage();
                        String type = msg[0].ReadString();
                        String payload = FrameToUnicodeString(msg[1]);

                        Action action = null;
                        try
                        {
                            action = Json.JsonConvert.DeserializeObject<Action>(
                                payload, new Json.JsonSerializerSettings { NullValueHandling = Json.NullValueHandling.Ignore });
                        }
                        catch
                        {
                            // ignore deserialization errors
                        }
                        if (action != null)
                        {
                            if (action.type == Action.ActionType.ComnsenseChange)
                            {
                                this.ApplyChange(action);
                            }
                            if (action.type == Action.ActionType.RangeRequest)
                            {
                                // read range and send event
                            }
                        }
                        err = default(ZError);
                        return true; 
                    })
                };
                
                try
                {
                    while (!ct.IsCancellationRequested)
                    {
                        if (!sockets.Poll(polls, ZPoll.In, ref messages, out error, Router.Interval))
                        {
                            if (error == ZError.EAGAIN)
                            {
                                Thread.Sleep(1);
                                continue;
                            }

                            if (error == ZError.ETERM)
                            {
                                break;
                            }

                            throw new ZException(error);
                        }
                    }
                }
                catch (ZException)
                {
                    if (!ct.IsCancellationRequested)
                    {
                        throw;
                    }
                }
            }
        }
    }

}
