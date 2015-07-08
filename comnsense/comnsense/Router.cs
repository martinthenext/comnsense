using System;
using System.Linq;
using System.Text;
using System.Threading;
using Microsoft.Office.Interop.Excel;
using Newtonsoft.Json;
using ZeroMQ;

namespace comnsense
{
    internal class Router
    {
        public const string AgentAddress = "tcp://127.0.0.1:8888";
        public static readonly TimeSpan Interval = TimeSpan.FromMilliseconds(500);

        private readonly ZContext _context;
        private readonly Application _excel;
        private readonly string _ident;

        // This socket should be accessible to every method 
        // in case you want to send Event right after Action has been received
        // private ZSocket agent;

        public Router(ZContext context, Application excel, string ident)
        {
            _context = context;
            _excel = excel;
            _ident = ident;
        }

        public static string FrameToUnicodeString(ZFrame frame)
        {
            var bytes = new byte[frame.Length];
            for (var i = 0; i < bytes.Length; i++)
                bytes[i] = (byte) frame.ReadByte();
            return Encoding.UTF8.GetString(bytes);
        }

        public static bool BitToBool(byte bitmask, int position)
        {
            return (bitmask & (1 << position)) != 0;
        }

        private Workbook GetWorkbook()
        {
            return (from Workbook wb in _excel.Workbooks
                    let id = new Ident(wb)
                    where _ident == id.ToString()
                    select wb).FirstOrDefault();
        }

        // TODO refactor, this is awful
        private void ApplyBorders(Borders borders, Range range)
        {
            if (borders.right != null)
            {
                var weight = (XlBorderWeight) borders.right[0];
                range.Borders[XlBordersIndex.xlEdgeRight].Weight = weight;

                var lineStyle = (XlLineStyle) borders.right[1];
                range.Borders[XlBordersIndex.xlEdgeRight].LineStyle = lineStyle;
            }

            if (borders.left != null)
            {
                var weight = (XlBorderWeight) borders.left[0];
                range.Borders[XlBordersIndex.xlEdgeLeft].Weight = weight;

                var lineStyle = (XlLineStyle) borders.left[1];
                range.Borders[XlBordersIndex.xlEdgeLeft].LineStyle = lineStyle;
            }

            if (borders.top != null)
            {
                var weight = (XlBorderWeight) borders.top[0];
                range.Borders[XlBordersIndex.xlEdgeTop].Weight = weight;

                var lineStyle = (XlLineStyle) borders.top[1];
                range.Borders[XlBordersIndex.xlEdgeTop].LineStyle = lineStyle;
            }

            if (borders.bottom != null)
            {
                var weight = (XlBorderWeight) borders.bottom[0];
                range.Borders[XlBordersIndex.xlEdgeBottom].Weight = weight;

                var lineStyle = (XlLineStyle) borders.bottom[1];
                range.Borders[XlBordersIndex.xlEdgeBottom].LineStyle = lineStyle;
            }
        }

        private void ApplyChange(Action action)
        {
            _excel.EnableEvents = false;
            try
            {
                if (action.workbook != _ident)
                    return;

                var wb = GetWorkbook();
                Worksheet ws = wb.Worksheets[action.sheet];

                foreach (var row in action.cells)
                {
                    foreach (var cell in row)
                    {
                        var range = ws.Range[cell.key];
                        range.Value2 = cell.value;

                        // Applying cell properties
                        // Matching Event.cs:90

                        if (cell.color != null)
                            range.Interior.ColorIndex = cell.color;

                        if (cell.font != null)
                            range.Font.Name = cell.font;

                        if (cell.fontstyle != null)
                        {
                            // Parsing format bitmask
                            range.Font.Bold = BitToBool(cell.fontstyle.Value, 0);
                            range.Font.Italic = BitToBool(cell.fontstyle.Value, 1);
                            range.Font.Underline = BitToBool(cell.fontstyle.Value, 2);
                        }

                        if (cell.borders != null)
                            ApplyBorders(cell.borders, range);
                    }
                }
            }
            finally
            {
                _excel.EnableEvents = true;
            }
        }

        // Get a response message to serve a request straight away
        private ZMessage ServeRangeRequest(Action action)
        {
            // TODO lousy boilerplate from above
            _excel.EnableEvents = false;
            try
            {
                if (action.workbook != _ident)
                    return null;
                var wb = GetWorkbook();
                Worksheet ws = wb.Worksheets[action.sheet];

                // boilerplate ends

                var rangeName = action.rangeName;

                // What is requested in addition to value?
                var isColorRequested = BitToBool(action.flags, 0);
                var isFontRequested = BitToBool(action.flags, 1);
                var isFontstyleRequested = BitToBool(action.flags, 2);
                var isBordersRequested = BitToBool(action.flags, 3);

                // Getting range
                var range = ws.Range[rangeName, Type.Missing];
                var cellsToSend = Event.GetCellsFromRange(
                    range,
                    isBordersRequested,
                    isFontRequested,
                    isColorRequested,
                    isFontstyleRequested);

                var responseEvent = new Event
                {
                    type = Event.EventType.RangeResponse,
                    workbook = _ident,
                    sheet = ws.Name,
                    cells = cellsToSend,
                };

                var eventJson = JsonConvert.SerializeObject(
                    responseEvent, 
                    Formatting.None,
                    new JsonSerializerSettings {NullValueHandling = NullValueHandling.Ignore});

                return new ZMessage {new ZFrame("event"), new ZFrame(Encoding.UTF8.GetBytes(eventJson))};
            }
            finally
            {
                _excel.EnableEvents = true;
            }
        }

        // This is run in a separate thread from ThidAddIn
        public void Run(CancellationToken ct)
        {
            using (var subscriber = new ZSocket(_context, ZSocketType.SUB))
            using (var agent = new ZSocket(_context, ZSocketType.DEALER))
            {
                subscriber.SetOption(ZSocketOption.SUBSCRIBE, _ident); // any events
                subscriber.Connect(EventPublisher.RouterAddress);

                agent.SetOption(ZSocketOption.IDENTITY, Guid.NewGuid().ToString());
                agent.Connect(AgentAddress);

                ZMessage[] messages = null;
                ZSocket[] sockets = {subscriber, agent};

                ZPollItem[] polls =
                {
                    // Receives publisher messages and forwards them
                    ZPollItem.Create((ZSocket sock, out ZMessage msg, out ZError err) =>
                    {
                        msg = sock.ReceiveMessage();
                        // We need the second frame
                        var frame = msg.Last();
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
                    // Receives Actions 
                    ZPollItem.Create((ZSocket sock, out ZMessage msg, out ZError err) =>
                    {
                        msg = sock.ReceiveMessage();
                        var payload = FrameToUnicodeString(msg[1]);

                        Action action = null;
                        try
                        {
                            action = JsonConvert.DeserializeObject<Action>(
                                payload,
                                new JsonSerializerSettings {NullValueHandling = NullValueHandling.Ignore});
                        }
                        catch
                        {
                            // ignore deserialization errors
                        }
                        if (action != null)
                        {
                            if (action.type == Action.ActionType.ComnsenseChange)
                                ApplyChange(action);
                            else if (action.type == Action.ActionType.RangeRequest)
                            {
                                var message = ServeRangeRequest(action);
                                agent.SendMessage(message);
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
                        ZError error;
                        if (sockets.Poll(polls, ZPoll.In, ref messages, out error, Interval))
                            continue;

                        if (Equals(error, ZError.EAGAIN))
                        {
                            Thread.Sleep(1);
                            continue;
                        }

                        if (Equals(error, ZError.ETERM))
                            break;

                        throw new ZException(error);
                    }
                }
                catch (ZException)
                {
                    if (!ct.IsCancellationRequested)
                        throw;
                }
            }
        }
    }
}