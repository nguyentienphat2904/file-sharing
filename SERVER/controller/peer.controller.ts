import { Request, Response } from "express";
import { PeerModel } from "../models/peer.models";

import bcrypt from "bcryptjs";

export class PeerController {

    async discover(req: Request, res: Response) {
        try {
            const peers = await PeerModel.find({});
            res.status(200).json({
                success: false,
                message: "Discover all Peers",
                data: peers
            });
            return;
        } catch (error: any) {
            res.status(500).json({
                success: false,
                message: error.message,
                data: []
            });
            return;
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
                return;
            } else {
                res.status(404).json({
                    success: false,
                    message: "Not Pong",
                    data: null
                });
                return;
            }
        } catch (error: any) {
            res.status(500).json({
                success: false,
                message: error.message,
                data: []
            });
            return;
        }
    }

    async register(req: Request, res: Response) {
        try {
            const { username, password, address, port } = req.body;
            if (!username || !password) {
                res.status(400).json({
                    message: "Username and Password are required"
                });
                return;
            }

            if (!address || !port) {
                res.status(400).json({
                    message: "Address and port are required"
                })
                return;
            }

            const existingUser = await PeerModel.findOne({ username });
            if (existingUser) {
                res.status(400).json({
                    message: "User already exists"
                });
                return;
            }

            const salt = await bcrypt.genSalt(10);
            const hashedPassword = await bcrypt.hash(password, salt);

            const newUser = new PeerModel({
                username,
                password: hashedPassword,
                address,
                port
            });
            await newUser.save();

            res.status(201).json({
                message: "User register successfully"
            });
            return;
        } catch (err) {
            res.status(500).json({ message: err });
            return;
        }
    }
}