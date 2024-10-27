import { Request, Response } from "express";
import { PeerModel } from "../models/peer.models";

export class PeerController {

    async create(req: Request, res: Response) {
        try {
            const peer = await PeerModel.create(req.body);
            res.status(200).json({
                success: true,
                message: "Create peer sucessfully",
                data: peer
            });
        } catch (error: any) {
            res.status(500).json({
                success: false,
                message: error.message,
                data: []
            });
        }
    }

    async discover(req: Request, res: Response) {
        try {
            const peers = await PeerModel.find({});
            res.status(200).json({
                success: false,
                message: "Discover all Peers",
                data: peers
            });
        } catch (error: any) {
            res.status(500).json({
                success: false,
                message: error.message,
                data: []
            });
        }
    }

    async ping(req: Request, res: Response) {
        try {
            const peer = await PeerModel.findOne({
                address: req.body.address,
                port: req.body.port
            });
            if (peer) {
                res.status(200).json({
                    success: false,
                    message: "Pong",
                    data: peer
                });
            } else {
                res.status(404).json({
                    success: false,
                    message: "Not Pong",
                    data: null
                });
            }
        } catch (error: any) {
            res.status(500).json({
                success: false,
                message: error.message,
                data: []
            });
        }
    }
}