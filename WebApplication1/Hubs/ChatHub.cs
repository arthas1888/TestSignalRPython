using Microsoft.AspNetCore.SignalR;
using Microsoft.Extensions.Logging;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace WebApplication1.Hubs
{
    public class ChatHub : Hub
    {
        #region Fields
        private readonly ILogger _logger;

        #endregion

        public ChatHub(
           ILogger<ChatHub> logger)
        {
            _logger = logger;
        }

        #region OnConnectedAsync
        public override async Task OnConnectedAsync()
        {
            _logger.LogInformation($"OnConnectedAsync conexion {Context.ConnectionId}");
            await base.OnConnectedAsync();
        }
        #endregion

        #region OnDisconnectedAsync
        public override async Task OnDisconnectedAsync(Exception exception)
        {
            _logger.LogInformation($"OnDisconnectedAsync conexion: {Context.ConnectionId}");
            await base.OnDisconnectedAsync(exception);
        }
        #endregion

        public async Task SendMessage(string user, string message)
        {
            await Clients.All.SendAsync("ReceiveMessage", user, message);
        }
    }
}