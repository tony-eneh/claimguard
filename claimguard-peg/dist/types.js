"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Action = void 0;
// Must match Solidity enum Action ordering
var Action;
(function (Action) {
    Action[Action["READ"] = 0] = "READ";
    Action[Action["APPEND"] = 1] = "APPEND";
    Action[Action["UPDATE"] = 2] = "UPDATE";
    Action[Action["DELETE"] = 3] = "DELETE";
    Action[Action["APPROVE"] = 4] = "APPROVE";
    Action[Action["SHARE"] = 5] = "SHARE";
})(Action || (exports.Action = Action = {}));
